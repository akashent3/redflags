"""Seed annual reports into database.

This script can:
1. Create sample reports with placeholder data (--mode sample)
2. Manually add a single report (--mode manual)
3. Fetch real annual reports from NSE API (--mode fetch)
4. Show database statistics (--mode stats)

Usage:
    # Sample mode (placeholder data)
    python scripts/seed_annual_reports.py --mode sample

    # Manual mode (single report)
    python scripts/seed_annual_reports.py --mode manual --company RELIANCE --year 2023 --pdf-url https://...

    # Fetch mode (real NSE data)
    python scripts/seed_annual_reports.py --mode fetch --company RELIANCE
    python scripts/seed_annual_reports.py --mode fetch --company TCS --years 5
    python scripts/seed_annual_reports.py --mode fetch --batch nifty50
    python scripts/seed_annual_reports.py --mode fetch --batch nifty500 --upload-r2

    # Dry run (test without changes)
    python scripts/seed_annual_reports.py --mode fetch --company RELIANCE --dry-run
    python scripts/seed_annual_reports.py --mode fetch --batch nifty50 --dry-run

    # Statistics mode
    python scripts/seed_annual_reports.py --mode stats
"""

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from dotenv import load_dotenv
from sqlalchemy import func

from app.database import SessionLocal
from app.models.annual_report import AnnualReport
from app.models.company import Company

# Import functions from fetch_annual_reports.py for real NSE data fetching
from fetch_annual_reports import (
    init_nse_session,
    fetch_annual_reports_from_nse,
    download_pdf,
    get_pdf_page_count,
    upload_to_r2,
)

load_dotenv()


# Sample annual reports data (placeholders)
SAMPLE_REPORTS = [
    {"symbol": "RELIANCE", "fiscal_year": 2023, "pdf_url": "https://example.com/reliance_ar_2023.pdf"},
    {"symbol": "RELIANCE", "fiscal_year": 2022, "pdf_url": "https://example.com/reliance_ar_2022.pdf"},
    {"symbol": "TCS", "fiscal_year": 2023, "pdf_url": "https://example.com/tcs_ar_2023.pdf"},
    {"symbol": "TCS", "fiscal_year": 2022, "pdf_url": "https://example.com/tcs_ar_2022.pdf"},
    {"symbol": "HDFCBANK", "fiscal_year": 2023, "pdf_url": "https://example.com/hdfc_ar_2023.pdf"},
    {"symbol": "INFY", "fiscal_year": 2023, "pdf_url": "https://example.com/infy_ar_2023.pdf"},
    {"symbol": "ICICIBANK", "fiscal_year": 2023, "pdf_url": "https://example.com/icici_ar_2023.pdf"},
    {"symbol": "BHARTIARTL", "fiscal_year": 2023, "pdf_url": "https://example.com/airtel_ar_2023.pdf"},
    {"symbol": "SBIN", "fiscal_year": 2023, "pdf_url": "https://example.com/sbi_ar_2023.pdf"},
    {"symbol": "HINDUNILVR", "fiscal_year": 2023, "pdf_url": "https://example.com/hul_ar_2023.pdf"},
]


def seed_sample_reports(dry_run: bool = False):
    """Seed sample annual reports."""
    db = SessionLocal()

    try:
        print("\n" + "=" * 60)
        print("[SEED] Seeding Sample Annual Reports")
        print("=" * 60)

        if dry_run:
            print("\n[WARNING]  DRY RUN MODE - No changes will be made\n")

        added = 0
        skipped = 0

        for report_data in SAMPLE_REPORTS:
            symbol = report_data['symbol']
            fiscal_year = report_data['fiscal_year']
            pdf_url = report_data['pdf_url']

            # Find company
            company = db.query(Company).filter(
                Company.nse_symbol == symbol
            ).first()

            if not company:
                print(f"[WARNING]  {symbol}: Company not found in database, skipping")
                skipped += 1
                continue

            # Check if report already exists
            existing = db.query(AnnualReport).filter(
                AnnualReport.company_id == company.id,
                AnnualReport.fiscal_year == fiscal_year
            ).first()

            if existing:
                print(f"[SKIP]  {symbol} FY{fiscal_year}: Already exists")
                skipped += 1
                continue

            if not dry_run:
                # Create annual report
                report = AnnualReport(
                    company_id=company.id,
                    fiscal_year=fiscal_year,
                    filing_date=datetime(fiscal_year, 9, 30),  # Assume Sept 30
                    pdf_url=pdf_url,
                    file_size_bytes=5000000,  # 5MB placeholder
                    pages_count=150,  # Placeholder
                    is_processed="pending",
                    extraction_method=None,
                )

                db.add(report)

            print(f"[OK] {symbol} FY{fiscal_year}: Added")
            added += 1

        if not dry_run:
            db.commit()

        # Summary
        print("\n" + "=" * 60)
        print("[STATS] SEEDING SUMMARY")
        print("=" * 60)
        print(f"[OK] Added:   {added}")
        print(f"[SKIP]  Skipped: {skipped}")
        print(f"[DATA] Total:   {len(SAMPLE_REPORTS)}")

        if dry_run:
            print("\n[WARNING]  This was a DRY RUN - no changes were made")

        return added

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        return 0

    finally:
        db.close()


def seed_manual_report(symbol: str, fiscal_year: int, pdf_url: str, dry_run: bool = False):
    """Manually seed a single annual report."""
    db = SessionLocal()

    try:
        print(f"\n[SEED] Adding report: {symbol} FY{fiscal_year}")

        # Find company
        company = db.query(Company).filter(
            Company.nse_symbol == symbol
        ).first()

        if not company:
            print(f"[ERROR] Company not found: {symbol}")
            return 0

        # Check if report already exists
        existing = db.query(AnnualReport).filter(
            AnnualReport.company_id == company.id,
            AnnualReport.fiscal_year == fiscal_year
        ).first()

        if existing:
            print(f"[SKIP]  Report already exists for {symbol} FY{fiscal_year}")
            return 0

        if not dry_run:
            # Create annual report
            report = AnnualReport(
                company_id=company.id,
                fiscal_year=fiscal_year,
                filing_date=datetime(fiscal_year, 9, 30),
                pdf_url=pdf_url,
                file_size_bytes=5000000,
                pages_count=150,
                is_processed="pending",
                extraction_method=None,
            )

            db.add(report)
            db.commit()

        print(f"[OK] Added report: {symbol} FY{fiscal_year}")
        return 1

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error: {e}")
        return 0

    finally:
        db.close()


def show_statistics():
    """Show statistics of seeded data."""
    db = SessionLocal()

    try:
        print("\n" + "=" * 60)
        print("[STATS] Database Statistics")
        print("=" * 60)

        # Count companies
        company_count = db.query(func.count(Company.id)).scalar()
        print(f"\n[DATA] Companies: {company_count}")

        # Count reports
        report_count = db.query(func.count(AnnualReport.id)).scalar()
        print(f"[REPORT] Annual Reports: {report_count}")

        # Reports by company
        print("\n[LIST] Reports by Company:")
        companies_with_reports = db.query(
            Company.nse_symbol,
            Company.name,
            func.count(AnnualReport.id).label('report_count')
        ).join(
            AnnualReport, Company.id == AnnualReport.company_id
        ).group_by(
            Company.id, Company.nse_symbol, Company.name
        ).order_by(
            func.count(AnnualReport.id).desc()
        ).limit(10).all()

        for symbol, name, count in companies_with_reports:
            print(f"   {symbol:<15} {name[:35]:<37} {count} reports")

        if report_count == 0:
            print("\n[WARNING]  No reports found. Run with --mode sample to add sample reports.")

    finally:
        db.close()


def get_batch_companies(batch_type: str, db):
    """
    Get list of companies for batch processing.

    Args:
        batch_type: 'nifty50', 'nifty500', or 'all'
        db: Database session

    Returns:
        List of Company objects
    """
    if batch_type == 'nifty50':
        return db.query(Company).filter(Company.is_nifty_50 == True).all()
    elif batch_type == 'nifty500':
        return db.query(Company).filter(Company.is_nifty_500 == True).all()
    else:  # all
        return db.query(Company).filter(Company.is_active == True).all()


def fetch_company_reports(company_symbol: str, years: int, session, db, upload_r2_flag: bool = False, dry_run: bool = False) -> int:
    """
    Fetch reports for a single company.

    Args:
        company_symbol: NSE symbol
        years: Number of years to fetch
        session: NSE session with cookies
        db: Database session
        upload_r2_flag: Upload to R2
        dry_run: Test mode

    Returns:
        Number of reports successfully downloaded
    """
    # Find company in database
    company = db.query(Company).filter(Company.nse_symbol == company_symbol).first()

    if not company:
        print(f"[WARNING] Company {company_symbol} not found in database")
        return 0

    # Fetch reports from NSE API
    reports = fetch_annual_reports_from_nse(company_symbol, session)

    if not reports:
        print(f"[WARNING] No reports found for {company_symbol}")
        return 0

    # Get most recent N years
    current_year = datetime.now().year
    recent_reports = [r for r in reports if current_year - r['year'] <= years]

    if not recent_reports:
        # Fallback to first N reports
        recent_reports = reports[:years]
    else:
        recent_reports = recent_reports[:years]

    downloaded_count = 0

    for report in recent_reports:
        year = report['year']
        pdf_url = report['url']

        # Check if report already exists
        existing = db.query(AnnualReport).filter(
            AnnualReport.company_id == company.id,
            AnnualReport.fiscal_year == year
        ).first()

        if existing:
            print(f"  [SKIP] FY{year}: Already exists")
            continue

        if dry_run:
            print(f"  [DRY-RUN] Would download FY{year}")
            downloaded_count += 1
            continue

        # Download PDF (pass session for cookie-based auth)
        local_path = download_pdf(pdf_url, company_symbol, year, session=session)

        if not local_path:
            print(f"  [FAIL] FY{year}: Download failed")
            continue

        # Get file size and page count
        file_size = Path(local_path).stat().st_size
        pages_count = get_pdf_page_count(local_path) if local_path else None

        if pages_count:
            print(f"[INFO] Extracted metadata: {pages_count} pages")

        # Upload to R2 if requested
        final_url = upload_to_r2(local_path, company_symbol, year) if upload_r2_flag else f"file://{local_path}"

        # Save to database
        report_record = AnnualReport(
            company_id=company.id,
            fiscal_year=year,
            filing_date=datetime(year, 9, 30) if year else None,
            pdf_url=final_url,
            file_size_bytes=file_size,
            pages_count=pages_count,
            is_processed="pending",
            extraction_method=None,
        )

        db.add(report_record)
        db.commit()

        print(f"  [OK] Saved to database")
        downloaded_count += 1

        # Rate limiting between reports
        time.sleep(1)

    return downloaded_count


def fetch_real_reports(company_symbol: str = None, batch: str = None, years: int = 3, upload_r2_flag: bool = False, dry_run: bool = False) -> dict:
    """
    Main orchestrator for fetching real annual reports from NSE API.

    Args:
        company_symbol: NSE symbol for single company
        batch: Batch type ('nifty50', 'nifty500', 'all')
        years: Number of recent years to fetch
        upload_r2_flag: Whether to upload to R2 storage
        dry_run: Test mode without downloads

    Returns:
        Dictionary with success/failure counts
    """
    db = SessionLocal()
    start_time = time.time()

    try:
        print("\n" + "=" * 60)
        print("[FETCH] Fetch Mode: Real NSE Data")
        print("=" * 60)

        if dry_run:
            print("\n[WARNING] DRY RUN MODE - No downloads or database changes\n")

        # Initialize NSE session
        print("\nInitializing NSE session...")
        session = init_nse_session()
        print("[OK] NSE session ready\n")

        results = {
            'total_companies': 0,
            'processed': 0,
            'reports_downloaded': 0,
            'reports_failed': 0,
            'duration_seconds': 0
        }

        # Get companies to process
        if company_symbol:
            companies = [db.query(Company).filter(Company.nse_symbol == company_symbol).first()]
            if not companies[0]:
                print(f"[ERROR] Company {company_symbol} not found in database")
                return results
            print(f"Company: {company_symbol}")
            print(f"Years: {years}")
            print(f"Upload to R2: {'Yes' if upload_r2_flag else 'No'}\n")
        elif batch:
            companies = get_batch_companies(batch, db)
            results['total_companies'] = len(companies)
            print(f"Batch: {batch.upper()}")
            print(f"Companies: {len(companies)}")
            print(f"Years per company: {years}")
            print(f"Expected PDFs: ~{len(companies) * years}")
            print(f"Upload to R2: {'Yes' if upload_r2_flag else 'No'}\n")

            if not dry_run:
                print(f"Estimated time: ~{len(companies) * 0.5:.0f} minutes")
                print("Starting in 3 seconds... (Ctrl+C to cancel)\n")
                time.sleep(3)
        else:
            print("[ERROR] Must specify --company or --batch")
            return results

        results['total_companies'] = len(companies)

        # Process companies
        for idx, company in enumerate(companies, 1):
            if not company:
                continue

            symbol = company.nse_symbol

            if batch:
                print(f"[{idx}/{len(companies)}] Processing {symbol}...")
            else:
                print("=" * 60)
                print(f"[COMPANY] {company.name} ({symbol})")
                print("=" * 60)

            try:
                downloaded = fetch_company_reports(
                    symbol, years, session, db, upload_r2_flag, dry_run
                )

                results['processed'] += 1
                results['reports_downloaded'] += downloaded

                if batch:
                    if downloaded == years:
                        print(f"[OK] {downloaded} reports downloaded\n")
                    elif downloaded > 0:
                        print(f"[WARNING] {downloaded} reports downloaded (some missing)\n")
                    else:
                        print(f"[FAIL] No reports downloaded\n")
                        results['reports_failed'] += 1

            except Exception as e:
                print(f"[ERROR] {symbol}: {e}\n")
                results['reports_failed'] += 1
                if not batch:
                    raise

            # Rate limiting between companies
            if batch and idx < len(companies):
                time.sleep(2)

        # Calculate duration
        duration = time.time() - start_time
        results['duration_seconds'] = duration

        # Summary
        print("\n" + "=" * 60)
        print("[SUMMARY] Fetch Summary")
        print("=" * 60)

        if batch:
            print(f"[OK] Companies processed: {results['processed']}/{results['total_companies']}")

        print(f"[OK] Reports downloaded: {results['reports_downloaded']}")

        if results['reports_failed'] > 0:
            print(f"[WARNING] Failed/Missing: {results['reports_failed']}")

        print(f"[INFO] Location: data/pdfs/")
        print(f"[INFO] Duration: {duration/60:.1f}m {duration%60:.0f}s")

        if dry_run:
            print("\n[WARNING] This was a DRY RUN - no downloads or changes made")
            print("Remove --dry-run to fetch reports")

        return results

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Fetch failed: {e}")
        import traceback
        traceback.print_exc()
        return results

    finally:
        db.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Seed annual reports into database')
    parser.add_argument('--mode', choices=['sample', 'manual', 'stats', 'fetch'], default='stats',
                        help='Seeding mode')
    parser.add_argument('--company', type=str, help='Company symbol (for manual/fetch mode)')
    parser.add_argument('--year', type=int, help='Fiscal year (for manual mode)')
    parser.add_argument('--pdf-url', type=str, help='PDF URL (for manual mode)')
    parser.add_argument('--batch', choices=['nifty50', 'nifty500', 'all'],
                        help='Batch fetch for index companies (use with --mode fetch)')
    parser.add_argument('--years', type=int, default=3,
                        help='Number of recent years to fetch (default: 3)')
    parser.add_argument('--upload-r2', action='store_true',
                        help='Upload PDFs to Cloudflare R2 (use with --mode fetch)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Run without making changes')

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("[REPORT] Annual Report Seeding Script")
    print("=" * 60)

    if args.mode == 'sample':
        added = seed_sample_reports(dry_run=args.dry_run)
        if added > 0 or args.dry_run:
            show_statistics()
            print("\n[OK] Seeding completed!")
            print("\nNext: Analyze reports with analysis API")
            return 0
        return 1

    elif args.mode == 'manual':
        if not all([args.company, args.year, args.pdf_url]):
            print("[ERROR] For manual mode, specify: --company --year --pdf-url")
            return 1

        added = seed_manual_report(args.company, args.year, args.pdf_url, args.dry_run)
        if added > 0:
            show_statistics()
            return 0
        return 1

    elif args.mode == 'fetch':
        if not args.company and not args.batch:
            print("[ERROR] For fetch mode, specify --company SYMBOL or --batch TYPE")
            print("\nExamples:")
            print("   • Single company: python scripts/seed_annual_reports.py --mode fetch --company RELIANCE")
            print("   • NIFTY 50 batch: python scripts/seed_annual_reports.py --mode fetch --batch nifty50")
            print("   • With R2 upload:  python scripts/seed_annual_reports.py --mode fetch --company TCS --upload-r2")
            return 1

        results = fetch_real_reports(
            company_symbol=args.company,
            batch=args.batch,
            years=args.years,
            upload_r2_flag=args.upload_r2,
            dry_run=args.dry_run
        )

        if results['reports_downloaded'] > 0 or args.dry_run:
            print("\nNext steps:")
            print("   1. View PDFs: ls data/pdfs/*.pdf")
            print("   2. Check database: SELECT * FROM annual_reports;")
            print("   3. Analyze companies: POST /api/v1/analyze/company/{company_id}")
            print("\n[OK] Fetch completed!")
            return 0
        return 1

    else:  # stats
        show_statistics()
        print("\nCommands:")
        print("   • Add sample reports: python scripts/seed_annual_reports.py --mode sample")
        print("   • Add manual report:  python scripts/seed_annual_reports.py --mode manual --company RELIANCE --year 2023 --pdf-url https://...")
        print("   • Fetch real reports: python scripts/seed_annual_reports.py --mode fetch --company RELIANCE")
        print("   • Batch fetch:        python scripts/seed_annual_reports.py --mode fetch --batch nifty50")
        return 0


if __name__ == "__main__":
    sys.exit(main())
