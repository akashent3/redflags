#!/usr/bin/env python3
"""
Standalone script to pre-seed the app with NIFTY 500 companies.

This script:
1. Fetches NIFTY 500 company list from FinEdge API
2. For each company:
   - Fetches latest annual report from NSE
   - Downloads PDF
   - Uploads to R2
   - Triggers analysis via Celery (or runs directly)

Usage:
    python seed_nifty500.py [--limit N] [--start INDEX] [--companies "RELIANCE,TCS,INFY"]
"""

import argparse
import logging
import os
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.company import Company
from app.models.annual_report import AnnualReport
from app.services.finedge_client import finedge_client
from app.services.nse_client import nse_client
from app.storage.r2_client import R2Client
from app.services.analysis_service_v2 import analysis_service_v2
import tempfile

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_nifty_500_symbols():
    """
    Get NIFTY 500 company symbols.

    For now, fetches all symbols from FinEdge and returns them.
    TODO: Filter to actual NIFTY 500 companies using a proper source.
    """
    try:
        all_symbols = finedge_client.get_all_symbols()

        # Filter to NSE symbols only
        nse_symbols = [
            s for s in all_symbols
            if s.get("exchange") == "NSE" or s.get("nse_code")
        ]

        logger.info(f"Found {len(nse_symbols)} NSE symbols")

        # Extract symbols
        symbols = []
        for s in nse_symbols:
            symbol = s.get("symbol") or s.get("nse_code")
            if symbol:
                symbols.append({
                    "symbol": symbol,
                    "name": s.get("name", symbol),
                })

        logger.info(f"Extracted {len(symbols)} NSE company symbols")
        return symbols

    except Exception as e:
        logger.error(f"Failed to fetch NIFTY 500 symbols: {e}")
        return []


def process_company(symbol_info: dict, db: SessionLocal, r2_client: R2Client, run_direct: bool = False):
    """
    Process a single company: fetch report, analyze.

    Args:
        symbol_info: Dict with 'symbol' and 'name'
        db: Database session
        r2_client: R2 storage client
        run_direct: If True, run analysis directly; if False, queue via Celery

    Returns:
        Dict with result info
    """
    symbol = symbol_info["symbol"]
    company_name = symbol_info["name"]

    logger.info(f"Processing {symbol} - {company_name}")

    try:
        # Step 1: Check if company already exists and has analysis
        existing_company = db.query(Company).filter(Company.nse_symbol == symbol).first()

        if existing_company:
            # Check if already has analysis
            existing_report = (
                db.query(AnnualReport)
                .filter(AnnualReport.company_id == existing_company.id)
                .first()
            )

            if existing_report and existing_report.is_processed == "completed":
                logger.info(f"  ✓ {symbol} already analyzed, skipping")
                return {"status": "skipped", "reason": "already_analyzed", "symbol": symbol}

        # Step 2: Fetch company profile from FinEdge
        try:
            profile = finedge_client.get_company_profile(symbol)
            industry = profile.get("industry", "Unknown")
            sector = profile.get("sector", "Unknown")
        except Exception as e:
            logger.warning(f"  Failed to fetch profile for {symbol}: {e}")
            industry = "Unknown"
            sector = "Unknown"

        # Step 3: Fetch latest annual report from NSE
        logger.info(f"  Fetching annual report from NSE...")
        annual_report_info = nse_client.get_latest_annual_report(symbol)

        if not annual_report_info or not annual_report_info.get("pdf_url"):
            logger.warning(f"  No annual report found for {symbol}")
            return {"status": "failed", "reason": "no_report", "symbol": symbol}

        pdf_url = annual_report_info["pdf_url"]
        fiscal_year = annual_report_info["year"]

        logger.info(f"  Found report: FY {fiscal_year}")

        # Step 4: Download PDF
        logger.info(f"  Downloading PDF...")
        pdf_bytes = nse_client.download_pdf(pdf_url)

        if not pdf_bytes:
            logger.warning(f"  Failed to download PDF for {symbol}")
            return {"status": "failed", "reason": "download_failed", "symbol": symbol}

        logger.info(f"  Downloaded {len(pdf_bytes)} bytes")

        # Step 5: Create/update company record
        if not existing_company:
            company = Company(
                name=company_name,
                nse_symbol=symbol,
                industry=industry,
                sector=sector,
                is_active=True,
            )
            db.add(company)
            db.commit()
            db.refresh(company)
            logger.info(f"  Created company record: {company.id}")
        else:
            company = existing_company
            logger.info(f"  Using existing company: {company.id}")

        # Step 6: Upload to R2
        logger.info(f"  Uploading to R2...")
        temp_fd, temp_pdf_path = tempfile.mkstemp(suffix=".pdf")
        os.write(temp_fd, pdf_bytes)
        os.close(temp_fd)

        try:
            object_key = f"reports/{company.id}/{fiscal_year}/annual_report.pdf"
            uploaded_url = r2_client.upload_file(temp_pdf_path, object_key)
            logger.info(f"  Uploaded to: {uploaded_url}")

            # Step 7: Create report record
            report = AnnualReport(
                company_id=company.id,
                fiscal_year=fiscal_year,
                pdf_url=uploaded_url,
                file_size_mb=len(pdf_bytes) / (1024 * 1024),
                is_processed="pending",
            )
            db.add(report)
            db.commit()
            db.refresh(report)
            logger.info(f"  Created report record: {report.id}")

            # Step 8: Trigger analysis
            if run_direct:
                logger.info(f"  Running analysis directly...")

                try:
                    analysis_result = analysis_service_v2.analyze_report(
                        db=db,
                        report_id=report.id,
                        pdf_path=temp_pdf_path,
                        company_symbol=symbol,
                        company_name=company_name,
                        fiscal_year=str(fiscal_year),
                    )

                    report.is_processed = "completed"
                    report.processed_at = analysis_result.analyzed_at
                    db.commit()

                    logger.info(
                        f"  ✓ Analysis complete: Risk {analysis_result.risk_score} ({analysis_result.risk_level}), "
                        f"{analysis_result.flags_triggered_count} flags triggered"
                    )

                    return {
                        "status": "success",
                        "symbol": symbol,
                        "risk_score": analysis_result.risk_score,
                        "risk_level": analysis_result.risk_level,
                    }

                except Exception as e:
                    logger.error(f"  Analysis failed for {symbol}: {e}")
                    report.is_processed = "failed"
                    db.commit()
                    return {"status": "failed", "reason": "analysis_failed", "symbol": symbol, "error": str(e)}
            else:
                logger.info(f"  Queueing analysis via Celery...")
                from app.tasks.analysis_tasks import analyze_report_task
                task = analyze_report_task.delay(str(report.id))
                logger.info(f"  ✓ Queued task: {task.id}")
                return {"status": "queued", "symbol": symbol, "task_id": task.id}

        finally:
            if os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)

    except Exception as e:
        logger.error(f"  Failed to process {symbol}: {e}", exc_info=True)
        return {"status": "failed", "symbol": symbol, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Pre-seed NIFTY 500 companies")
    parser.add_argument("--limit", type=int, help="Limit number of companies to process")
    parser.add_argument("--start", type=int, default=0, help="Start index (for resuming)")
    parser.add_argument("--companies", type=str, help="Comma-separated list of specific symbols to process")
    parser.add_argument("--direct", action="store_true", help="Run analysis directly instead of queueing")
    parser.add_argument("--delay", type=int, default=5, help="Delay in seconds between companies (to avoid rate limits)")

    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("NIFTY 500 Pre-Seeding Script")
    logger.info("=" * 80)

    # Initialize clients
    db = SessionLocal()
    r2_client = R2Client()

    try:
        # Get company list
        if args.companies:
            # Specific companies
            symbols = [{"symbol": s.strip(), "name": s.strip()} for s in args.companies.split(",")]
            logger.info(f"Processing {len(symbols)} specific companies: {args.companies}")
        else:
            # All NIFTY 500
            symbols = get_nifty_500_symbols()
            logger.info(f"Processing all {len(symbols)} NSE companies")

        # Apply limit and start
        if args.start > 0:
            symbols = symbols[args.start:]
            logger.info(f"Starting from index {args.start}")

        if args.limit:
            symbols = symbols[:args.limit]
            logger.info(f"Limited to {args.limit} companies")

        logger.info(f"Total to process: {len(symbols)} companies")
        logger.info("=" * 80)

        # Process each company
        results = {
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "queued": 0,
        }

        for i, symbol_info in enumerate(symbols, 1):
            logger.info(f"\n[{i}/{len(symbols)}] Processing {symbol_info['symbol']}...")

            result = process_company(symbol_info, db, r2_client, run_direct=args.direct)

            if result["status"] == "success":
                results["success"] += 1
            elif result["status"] == "failed":
                results["failed"] += 1
            elif result["status"] == "skipped":
                results["skipped"] += 1
            elif result["status"] == "queued":
                results["queued"] += 1

            # Delay between companies
            if i < len(symbols) and args.delay > 0:
                logger.info(f"  Waiting {args.delay}s before next company...")
                time.sleep(args.delay)

        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total companies: {len(symbols)}")
        logger.info(f"Success: {results['success']}")
        logger.info(f"Failed: {results['failed']}")
        logger.info(f"Skipped: {results['skipped']}")
        logger.info(f"Queued: {results['queued']}")
        logger.info("=" * 80)

    finally:
        db.close()


if __name__ == "__main__":
    main()
