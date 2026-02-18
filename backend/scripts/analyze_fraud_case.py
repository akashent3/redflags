#!/usr/bin/env python3
"""
Admin script to analyze fraud case PDFs and store in database.

Usage:
    python scripts/analyze_fraud_case.py \
        --symbol SATYAM \
        --pdf path/to/satyam_2009.pdf \
        --year 2009 \
        --fraud-type "Accounting Fraud" \
        --stock-decline -97.4 \
        --market-cap-lost 14000

This script:
1. Uploads PDF to R2 storage
2. Fetches financial data from FinEdge API (if symbol available)
3. Calculates API flags (21 non-bank or 8 bank flags)
4. Analyzes PDF with Gemini AI (23 non-bank or 25 bank flags)
5. Combines flags and saves to fraud_cases table
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models.fraud_case import FraudCase
from app.services.finedge_client import finedge_client
from app.services.api_flags import calculate_api_flags
from app.services.gemini_analyzer import analyze_pdf_with_gemini
from app.services.r2_storage import r2_client
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def upload_pdf_to_r2(pdf_path: str, company_name: str, year: int) -> str:
    """Upload PDF to R2 storage."""
    try:
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()

        # Create object key: fraud_cases/{year}/{company_name}.pdf
        clean_company_name = company_name.lower().replace(' ', '_')
        object_key = f"fraud_cases/{year}/{clean_company_name}.pdf"

        logger.info(f"Uploading PDF to R2: {object_key}")
        pdf_url = r2_client.upload_file(pdf_bytes, object_key)
        logger.info(f"✅ PDF uploaded successfully: {pdf_url}")

        return pdf_url
    except Exception as e:
        logger.error(f"Failed to upload PDF to R2: {e}")
        raise


def fetch_finedge_data(symbol: str) -> Optional[Dict]:
    """Fetch financial data from FinEdge API."""
    try:
        logger.info(f"Fetching financial data for {symbol} from FinEdge API...")

        # Get company profile
        profile = finedge_client.get_company_profile(symbol)
        if not profile:
            logger.warning(f"No profile found for {symbol}")
            return None

        # Get financial data (last 3 years)
        financial_data = {}
        for year_offset in [0, 1, 2]:
            try:
                pl = finedge_client.get_pl_statement(symbol, year_offset)
                bs = finedge_client.get_balance_sheet(symbol, year_offset)
                cf = finedge_client.get_cash_flow(symbol, year_offset)

                if pl and bs and cf:
                    financial_data[f'year_{year_offset}'] = {
                        'pl': pl,
                        'bs': bs,
                        'cf': cf
                    }
            except:
                continue

        return {
            'profile': profile,
            'financial_data': financial_data,
            'sector': profile.get('sector'),
            'industry': profile.get('industry')
        }
    except Exception as e:
        logger.warning(f"Failed to fetch FinEdge data: {e}")
        return None


def analyze_fraud_case_pdf(
    symbol: str,
    pdf_path: str,
    year: int,
    fraud_type: str,
    stock_decline_percent: float,
    market_cap_lost_cr: float,
    company_name: Optional[str] = None
) -> FraudCase:
    """
    Analyze fraud case PDF using same logic as regular analysis.

    Returns FraudCase object ready to be saved to database.
    """
    db = SessionLocal()

    try:
        # Step 1: Upload PDF to R2
        logger.info("=" * 60)
        logger.info(f"ANALYZING FRAUD CASE: {company_name or symbol} ({year})")
        logger.info("=" * 60)

        pdf_url = upload_pdf_to_r2(pdf_path, company_name or symbol, year)

        # Step 2: Fetch financial data from FinEdge
        finedge_data = fetch_finedge_data(symbol)

        if finedge_data:
            sector = finedge_data.get('sector')
            industry = finedge_data.get('industry')
            actual_company_name = finedge_data['profile'].get('name', company_name or symbol)
        else:
            sector = None
            industry = None
            actual_company_name = company_name or symbol

        # Step 3: Calculate API flags (if financial data available)
        api_flags = []
        if finedge_data and finedge_data.get('financial_data'):
            logger.info("Calculating API flags from FinEdge data...")
            try:
                # Determine if bank/NBFC
                is_bank = sector and ('bank' in sector.lower() or 'nbfc' in sector.lower())

                api_flags = calculate_api_flags(
                    finedge_data['financial_data'],
                    is_bank=is_bank
                )
                logger.info(f"✅ API flags calculated: {len(api_flags)} total")
            except Exception as e:
                logger.warning(f"Failed to calculate API flags: {e}")

        # Step 4: Analyze PDF with Gemini
        logger.info("Analyzing PDF with Gemini AI...")
        gemini_flags = []
        try:
            with open(pdf_path, 'rb') as f:
                pdf_bytes = f.read()

            # Determine if bank/NBFC
            is_bank = sector and ('bank' in sector.lower() or 'nbfc' in sector.lower())

            gemini_flags = analyze_pdf_with_gemini(
                pdf_bytes,
                actual_company_name,
                year,
                is_bank=is_bank
            )
            logger.info(f"✅ Gemini flags calculated: {len(gemini_flags)} total")
        except Exception as e:
            logger.error(f"Failed to analyze PDF with Gemini: {e}")
            raise

        # Step 5: Combine all flags
        all_flags = api_flags + gemini_flags
        triggered_flags = [f for f in all_flags if f.get('triggered', False)]

        logger.info(f"✅ Total flags: {len(all_flags)}")
        logger.info(f"✅ Triggered flags: {len(triggered_flags)}")

        # Step 6: Format red flags for database
        red_flags_detected = []
        for flag in triggered_flags:
            red_flags_detected.append({
                'flag_number': flag.get('flag_number'),
                'flag_name': flag.get('flag_name'),
                'category': flag.get('category'),
                'severity': flag.get('severity'),
                'evidence': flag.get('evidence', 'Evidence found in analysis'),
                'when_visible': '2 years before fraud'  # Default - can be customized
            })

        # Extract primary flags (top 3 by severity)
        primary_flags = [
            f['flag_name'] for f in sorted(
                triggered_flags,
                key=lambda x: {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}.get(x.get('severity', 'LOW'), 4)
            )[:3]
        ]

        # Step 7: Create FraudCase object
        case_id = f"{actual_company_name.lower().replace(' ', '-')}-{year}"

        fraud_case = FraudCase(
            case_id=case_id,
            company_name=actual_company_name,
            year=year,
            sector=sector,
            industry=industry,
            fraud_type=fraud_type,
            stock_decline_percent=stock_decline_percent,
            market_cap_lost_cr=market_cap_lost_cr,
            primary_flags=primary_flags,
            red_flags_detected=red_flags_detected,
            pdf_url=pdf_url,
            # These can be manually updated later via admin UI
            timeline=None,
            what_investors_missed=None,
            lessons_learned=None,
            outcome=f"Stock declined by {stock_decline_percent}%, market cap lost ₹{market_cap_lost_cr} crores",
            regulatory_action="To be updated"
        )

        # Step 8: Save to database
        existing = db.query(FraudCase).filter(FraudCase.case_id == case_id).first()
        if existing:
            logger.warning(f"⚠️  Fraud case already exists: {case_id}")
            logger.info("Updating existing fraud case...")

            # Update existing case
            existing.company_name = actual_company_name
            existing.sector = sector
            existing.industry = industry
            existing.fraud_type = fraud_type
            existing.stock_decline_percent = stock_decline_percent
            existing.market_cap_lost_cr = market_cap_lost_cr
            existing.primary_flags = primary_flags
            existing.red_flags_detected = red_flags_detected
            existing.pdf_url = pdf_url
            existing.outcome = fraud_case.outcome

            db.commit()
            db.refresh(existing)
            fraud_case = existing
        else:
            db.add(fraud_case)
            db.commit()
            db.refresh(fraud_case)

        logger.info("=" * 60)
        logger.info(f"✅ FRAUD CASE SAVED: {fraud_case.id}")
        logger.info(f"   Case ID: {fraud_case.case_id}")
        logger.info(f"   Company: {fraud_case.company_name}")
        logger.info(f"   Year: {fraud_case.year}")
        logger.info(f"   Triggered Flags: {len(red_flags_detected)}")
        logger.info("=" * 60)

        return fraud_case

    except Exception as e:
        logger.error(f"❌ Failed to analyze fraud case: {e}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description='Analyze fraud case PDF and store in database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/analyze_fraud_case.py \\
      --symbol SATYAM \\
      --pdf fraud_cases/satyam_2009.pdf \\
      --year 2009 \\
      --fraud-type "Accounting Fraud" \\
      --stock-decline -97.4 \\
      --market-cap-lost 14000

  python scripts/analyze_fraud_case.py \\
      --symbol DHFL \\
      --pdf fraud_cases/dhfl_2019.pdf \\
      --year 2019 \\
      --company-name "Dewan Housing Finance" \\
      --fraud-type "Diversion of Funds" \\
      --stock-decline -99.8 \\
      --market-cap-lost 35000
        """
    )

    parser.add_argument('--symbol', required=True, help='NSE symbol for FinEdge API')
    parser.add_argument('--pdf', required=True, help='Path to PDF file')
    parser.add_argument('--year', type=int, required=True, help='Year of fraud (e.g., 2009)')
    parser.add_argument('--fraud-type', required=True, help='Type of fraud (e.g., "Accounting Fraud")')
    parser.add_argument('--stock-decline', type=float, required=True, help='Stock decline percentage (e.g., -97.4)')
    parser.add_argument('--market-cap-lost', type=float, required=True, help='Market cap lost in crores')
    parser.add_argument('--company-name', help='Company name (if different from symbol)')

    args = parser.parse_args()

    # Validate PDF path
    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        logger.error(f"❌ PDF file not found: {pdf_path}")
        sys.exit(1)

    try:
        fraud_case = analyze_fraud_case_pdf(
            symbol=args.symbol,
            pdf_path=str(pdf_path),
            year=args.year,
            fraud_type=args.fraud_type,
            stock_decline_percent=args.stock_decline,
            market_cap_lost_cr=args.market_cap_lost,
            company_name=args.company_name
        )

        print("\n" + "=" * 60)
        print("✅ SUCCESS!")
        print("=" * 60)
        print(f"Fraud case saved to database:")
        print(f"  ID: {fraud_case.id}")
        print(f"  Case ID: {fraud_case.case_id}")
        print(f"  Company: {fraud_case.company_name}")
        print(f"  Triggered Flags: {len(fraud_case.red_flags_detected)}")
        print("=" * 60)

    except Exception as e:
        logger.error(f"❌ Script failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
