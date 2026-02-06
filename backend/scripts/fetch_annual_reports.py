"""Fetch and download annual reports from NSE API.

This script uses NSE India's official API to fetch annual reports:
API: https://www.nseindia.com/api/annual-reports?index=equities&symbol=RELIANCE

This script:
1. Fetches annual report list from NSE API
2. Downloads last 3 years of reports
3. Uploads to Cloudflare R2 or saves locally
4. Creates database records

Usage:
    # Download for specific company
    python scripts/fetch_annual_reports.py --company RELIANCE --years 3

    # Download for all NIFTY 50
    python scripts/fetch_annual_reports.py --batch nifty50 --years 3

    # Download for all NIFTY 500
    python scripts/fetch_annual_reports.py --batch nifty500 --years 3 --upload-r2

References:
    - https://github.com/bshada/nse-bse-api
    - https://github.com/hi-imcodeman/stock-nse-india
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

import requests
from dotenv import load_dotenv

from app.database import SessionLocal
from app.models.annual_report import AnnualReport
from app.models.company import Company

load_dotenv()

# NSE API Configuration
NSE_BASE_URL = "https://www.nseindia.com"
NSE_ANNUAL_REPORTS_API = f"{NSE_BASE_URL}/api/annual-reports"

# NSE requires these headers to avoid 403 errors
NSE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.nseindia.com/companies-listing/corporate-filings-annual-reports',
    'Connection': 'keep-alive',
}


def init_nse_session():
    """
    Initialize NSE session with cookies.
    NSE requires cookies from a page visit before API calls work.
    The key cookie is 'bm_sv' set by Akamai Bot Manager.
    """
    session = requests.Session()
    session.headers.update(NSE_HEADERS)

    # Try multiple pages to get session cookies - NSE sometimes blocks one but not others
    cookie_pages = [
        NSE_BASE_URL,
        f"{NSE_BASE_URL}/option-chain",
        f"{NSE_BASE_URL}/companies-listing/corporate-filings-annual-reports",
    ]

    for page_url in cookie_pages:
        try:
            response = session.get(page_url, timeout=10)
            if response.status_code == 200:
                # Check if we got cookies
                if session.cookies:
                    print(f"✅ Got session cookies from {page_url}")
                    return session
            else:
                print(f"⚠️  {page_url} returned status {response.status_code}")
        except Exception as e:
            print(f"⚠️  Failed to reach {page_url}: {e}")

        time.sleep(1)  # Small delay between attempts

    # Return session anyway - some calls might still work
    if session.cookies:
        print(f"⚠️  Got partial cookies, proceeding anyway")
    else:
        print(f"⚠️  No cookies obtained. API calls may fail with 401/403")
    return session


def fetch_annual_reports_from_nse(symbol: str, session: requests.Session) -> list:
    """
    Fetch annual reports for a company from NSE API.

    Args:
        symbol: NSE stock symbol (e.g., 'RELIANCE')
        session: Requests session with NSE cookies

    Returns:
        List of dicts with report metadata:
        [
            {
                'year': '2023',
                'title': 'Annual Report 2022-23',
                'url': 'https://...',
                'date': '2023-09-30'
            }
        ]
    """
    print(f"📡 Fetching reports for {symbol} from NSE API...")

    try:
        # Build API URL
        api_url = f"{NSE_ANNUAL_REPORTS_API}?index=equities&symbol={symbol}"

        # Make API request
        response = session.get(api_url, timeout=15)

        if response.status_code != 200:
            print(f"❌ NSE API returned status {response.status_code}")
            if response.status_code == 403:
                print("   Try refreshing NSE session cookies")
            return []

        # Parse JSON response
        # NSE API returns: {"data": [{"companyName": "...", "fromYr": "2023", "toYr": "2024", "fileName": "https://...", ...}]}
        data = response.json()

        # Extract the data array from response
        report_list = None
        if isinstance(data, dict) and 'data' in data:
            report_list = data['data']
        elif isinstance(data, list):
            report_list = data  # Fallback if API returns plain list

        if not report_list:
            print(f"⚠️  No reports found for {symbol}")
            return []

        reports = []
        for report in report_list:
            # NSE API fields: fromYr, toYr, fileName, companyName, broadcast_dttm
            from_yr = report.get('fromYr', '')
            to_yr = report.get('toYr', '')

            # The fiscal year is the ending year (e.g., fromYr=2023, toYr=2024 -> FY2024)
            try:
                year = int(to_yr) if to_yr else int(from_yr) if from_yr else extract_year_from_report(report)
            except (ValueError, TypeError):
                year = extract_year_from_report(report)

            pdf_url = report.get('fileName', '')
            title = f"Annual Report {from_yr}-{to_yr}" if from_yr and to_yr else f"Annual Report {year}"
            date_str = report.get('broadcast_dttm', report.get('disseminationDateTime', ''))

            reports.append({
                'year': year,
                'title': title,
                'url': pdf_url,
                'date': date_str,
                'raw': report  # Keep raw data for debugging
            })

        print(f"✅ Found {len(reports)} report(s)")
        for r in reports:
            print(f"   • FY{r['year']}: {r['title'][:60]}")

        return reports

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON response: {e}")
        return []
    except Exception as e:
        print(f"❌ Error fetching from NSE API: {e}")
        return []


def extract_year_from_report(report: dict) -> int:
    """Extract fiscal year from NSE report metadata."""
    import re

    # Try fromYr/toYr first (NSE API format)
    to_yr = report.get('toYr', '')
    if to_yr:
        try:
            return int(to_yr)
        except (ValueError, TypeError):
            pass

    from_yr = report.get('fromYr', '')
    if from_yr:
        try:
            return int(from_yr) + 1  # fiscal year ending
        except (ValueError, TypeError):
            pass

    # Try to extract from description/title
    text = report.get('desc', '') + ' ' + report.get('title', '') + ' ' + report.get('companyName', '')

    # Look for patterns like "2022-23", "2023", "FY23"
    patterns = [
        r'20(\d{2})-?(\d{2})',  # 2022-23
        r'FY\s*(\d{2})',  # FY23
        r'(20\d{2})',  # 2023
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            if len(match.groups()) > 1:
                # For ranges like 2022-23, return ending year (2023)
                return 2000 + int(match.group(2))
            else:
                year_str = match.group(1)
                if len(year_str) == 2:
                    return 2000 + int(year_str)
                else:
                    return int(year_str)

    # Fallback: try to extract from date field
    date_str = report.get('date', report.get('filing_date', ''))
    if date_str:
        try:
            year = int(date_str.split('-')[0])
            return year
        except:
            pass

    # Default to current year if nothing found
    return datetime.now().year


def download_pdf(url: str, company_symbol: str, year: int, output_dir: str = 'data/pdfs', session: requests.Session = None) -> str:
    """
    Download PDF from NSE archives.

    Args:
        url: PDF URL (typically on nsearchives.nseindia.com)
        company_symbol: Company symbol
        year: Fiscal year
        output_dir: Output directory
        session: Optional requests session with NSE cookies

    Returns:
        Local file path or None if failed
    """
    print(f"⬇️  Downloading {company_symbol} FY{year}...")

    try:
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Generate filename
        filename = f"{company_symbol}_AR_{year}.pdf"
        filepath = Path(output_dir) / filename

        # Skip if already exists
        if filepath.exists():
            file_size = filepath.stat().st_size
            if file_size > 100000:  # > 100KB
                print(f"⏭️  Already exists ({file_size / 1024 / 1024:.2f} MB)")
                return str(filepath)

        # Make URL absolute if needed
        if not url.startswith('http'):
            url = NSE_BASE_URL + url

        # Download - use session if provided, otherwise plain request with headers
        if session:
            response = session.get(url, timeout=60, stream=True)
        else:
            response = requests.get(url, headers=NSE_HEADERS, timeout=60, stream=True)

        if response.status_code != 200:
            print(f"❌ Download failed: HTTP {response.status_code}")
            return None

        # Check if response is actually a PDF
        content_type = response.headers.get('Content-Type', '')
        if 'pdf' not in content_type.lower() and 'application/octet-stream' not in content_type.lower():
            print(f"⚠️  Response is not a PDF: {content_type}")
            # Still try to save - some servers don't set Content-Type correctly

        # Save to file
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        file_size = filepath.stat().st_size

        if file_size < 100000:  # Less than 100KB is suspicious
            print(f"⚠️  Downloaded file is too small ({file_size} bytes), might be error page")
            filepath.unlink()  # Delete
            return None

        print(f"✅ Downloaded {file_size / 1024 / 1024:.2f} MB")
        return str(filepath)

    except Exception as e:
        print(f"❌ Download error: {e}")
        return None


def upload_to_r2(local_path: str, company_symbol: str, year: int) -> str:
    """
    Upload PDF to Cloudflare R2.

    Returns:
        R2 public URL or local path if R2 not configured
    """
    print(f"☁️  Uploading to R2...")

    try:
        # Check if R2 is configured
        if not os.getenv('R2_ACCESS_KEY_ID'):
            print(f"⚠️  R2 not configured, using local path")
            return f"file://{local_path}"

        # Import R2 client
        from app.storage.r2_client import r2_client

        with open(local_path, 'rb') as f:
            pdf_bytes = f.read()

        # Upload to R2
        key = f"annual_reports/{company_symbol}/{year}/annual_report_{year}.pdf"
        url = r2_client.upload_file(pdf_bytes, key, 'application/pdf')

        print(f"✅ Uploaded to R2")
        return url

    except ImportError:
        print(f"⚠️  R2 client not available, using local path")
        return f"file://{local_path}"
    except Exception as e:
        print(f"⚠️  R2 upload failed: {e}")
        return f"file://{local_path}"


def get_pdf_page_count(pdf_path: str) -> int:
    """Get page count from PDF using PyMuPDF."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        page_count = len(doc)
        doc.close()
        return page_count
    except:
        return None


def save_to_database(company_id: str, year: int, pdf_url: str, file_size: int, pages: int = None):
    """Save annual report record to database."""
    db = SessionLocal()

    try:
        # Check if already exists
        existing = db.query(AnnualReport).filter(
            AnnualReport.company_id == company_id,
            AnnualReport.fiscal_year == year
        ).first()

        if existing:
            print(f"⏭️  Report already in database (updating URL)")
            existing.pdf_url = pdf_url
            existing.file_size_bytes = file_size
            if pages:
                existing.pages_count = pages
            db.commit()
            return

        # Create new record
        report = AnnualReport(
            company_id=company_id,
            fiscal_year=year,
            filing_date=datetime(year, 9, 30),  # Assume Sept 30
            pdf_url=pdf_url,
            file_size_bytes=file_size,
            pages_count=pages,
            is_processed="pending",
            extraction_method=None,
        )

        db.add(report)
        db.commit()

        print(f"✅ Saved to database")

    except Exception as e:
        db.rollback()
        print(f"❌ Database error: {e}")

    finally:
        db.close()


def fetch_for_company(company_symbol: str, num_years: int = 3, upload_r2: bool = False, session: requests.Session = None):
    """
    Fetch annual reports for a specific company using NSE API.

    Args:
        company_symbol: NSE symbol (e.g., 'RELIANCE')
        num_years: Number of recent years to download
        upload_r2: Upload to R2 storage
        session: NSE session with cookies

    Returns:
        Number of reports downloaded
    """
    db = SessionLocal()

    try:
        # Find company in database
        company = db.query(Company).filter(
            Company.nse_symbol == company_symbol
        ).first()

        if not company:
            print(f"❌ Company not found in database: {company_symbol}")
            print(f"   Run seed_companies.py first")
            return 0

        print(f"\n{'=' * 60}")
        print(f"📊 {company.name} ({company_symbol})")
        print(f"{'=' * 60}")

        # Initialize NSE session if not provided
        if not session:
            session = init_nse_session()

        # Fetch reports from NSE API
        reports = fetch_annual_reports_from_nse(company_symbol, session)

        if not reports:
            print(f"⚠️  No reports found via NSE API")
            return 0

        # Download reports (limit to num_years)
        current_year = datetime.now().year
        recent_reports = [r for r in reports if current_year - r['year'] <= num_years]

        if not recent_reports:
            print(f"⚠️  No recent reports found (last {num_years} years)")
            recent_reports = reports[:num_years]  # Take most recent ones

        downloaded = 0
        for report in recent_reports[:num_years]:
            year = report['year']
            pdf_url = report['url']

            if not pdf_url:
                print(f"⚠️  FY{year}: No PDF URL available")
                continue

            # Download PDF (pass session for cookie-based auth)
            local_path = download_pdf(pdf_url, company_symbol, year, session=session)

            if not local_path:
                continue

            # Get page count
            pages = get_pdf_page_count(local_path)

            # Upload to R2 if requested
            final_url = pdf_url
            if upload_r2:
                r2_url = upload_to_r2(local_path, company_symbol, year)
                if r2_url and not r2_url.startswith('file://'):
                    final_url = r2_url
                else:
                    final_url = f"file://{local_path}"
            else:
                final_url = f"file://{local_path}"

            # Save to database
            file_size = Path(local_path).stat().st_size if Path(local_path).exists() else 0
            save_to_database(str(company.id), year, final_url, file_size, pages)

            downloaded += 1

            # Rate limiting to be nice to NSE
            time.sleep(2)

        return downloaded

    finally:
        db.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Fetch annual reports from NSE API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Download for single company (last 3 years)
    python scripts/fetch_annual_reports.py --company RELIANCE --years 3

    # Download for NIFTY 50 (last 3 years each)
    python scripts/fetch_annual_reports.py --batch nifty50 --years 3

    # Download for all NIFTY 500 with R2 upload
    python scripts/fetch_annual_reports.py --batch nifty500 --years 3 --upload-r2

    # Dry run (no downloads)
    python scripts/fetch_annual_reports.py --company TCS --dry-run
        """
    )
    parser.add_argument('--company', type=str, help='Company NSE symbol (e.g., RELIANCE)')
    parser.add_argument('--years', type=int, default=3, help='Number of recent years to download (default: 3)')
    parser.add_argument('--batch', choices=['nifty50', 'nifty500', 'all'], help='Download for entire index')
    parser.add_argument('--upload-r2', action='store_true', help='Upload PDFs to Cloudflare R2')
    parser.add_argument('--dry-run', action='store_true', help='Test API without downloading')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay between requests in seconds (default: 2)')

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("📄 NSE Annual Report Fetcher")
    print("=" * 60)
    print(f"Source: NSE India API")
    print(f"Endpoint: {NSE_ANNUAL_REPORTS_API}")
    print("=" * 60)

    # Initialize NSE session once
    session = init_nse_session()

    if args.company:
        # Single company
        if args.dry_run:
            print("\n🧪 DRY RUN MODE - Testing API only\n")
            reports = fetch_annual_reports_from_nse(args.company, session)
            if reports:
                print(f"\n✅ API working! Found {len(reports)} reports")
                print("Remove --dry-run to download")
            return 0

        downloaded = fetch_for_company(args.company, args.years, args.upload_r2, session)

        if downloaded > 0:
            print(f"\n✅ Successfully downloaded {downloaded} report(s)")
            print(f"\nNext steps:")
            print(f"  1. Check: ls backend/data/pdfs/{args.company}*.pdf")
            print(f"  2. Verify in database: SELECT * FROM annual_reports WHERE company_id IN (SELECT id FROM companies WHERE nse_symbol = '{args.company}');")
            print(f"  3. Analyze: POST /api/v1/analyze/company/{{company_id}}")
        else:
            print(f"\n⚠️  No reports downloaded")

    elif args.batch:
        # Batch download
        db = SessionLocal()

        try:
            if args.batch == 'nifty50':
                companies = db.query(Company).filter(Company.is_nifty_50 == True).all()
            elif args.batch == 'nifty500':
                companies = db.query(Company).filter(Company.is_nifty_500 == True).all()
            else:  # all
                companies = db.query(Company).filter(Company.is_active == True).all()

            print(f"\n📊 Batch download for {len(companies)} companies")
            print(f"Years per company: {args.years}")
            print(f"Estimated time: {len(companies) * args.years * (args.delay + 30)} seconds")
            print(f"Estimated PDFs: {len(companies) * args.years}")
            print("\nStarting in 3 seconds... (Ctrl+C to cancel)")
            time.sleep(3)

            total_downloaded = 0
            total_failed = 0

            for idx, company in enumerate(companies, 1):
                print(f"\n[{idx}/{len(companies)}] Processing {company.nse_symbol}...")

                try:
                    downloaded = fetch_for_company(company.nse_symbol, args.years, args.upload_r2, session)
                    total_downloaded += downloaded

                    if downloaded == 0:
                        total_failed += 1

                except KeyboardInterrupt:
                    print("\n⏸️  Interrupted by user")
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
                    total_failed += 1

                # Rate limiting between companies
                if idx < len(companies):
                    time.sleep(args.delay)

            print(f"\n{'=' * 60}")
            print(f"📊 BATCH DOWNLOAD SUMMARY")
            print(f"={'=' * 60}")
            print(f"✅ Companies processed: {idx}/{len(companies)}")
            print(f"✅ Reports downloaded: {total_downloaded}")
            print(f"❌ Failed: {total_failed}")
            print(f"📁 PDFs location: backend/data/pdfs/")

        finally:
            db.close()

    else:
        print("❌ Please specify --company or --batch")
        print("\nExamples:")
        print("  python scripts/fetch_annual_reports.py --company RELIANCE --years 3")
        print("  python scripts/fetch_annual_reports.py --batch nifty50 --years 3")
        print("  python scripts/fetch_annual_reports.py --batch nifty500 --years 3 --upload-r2")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
