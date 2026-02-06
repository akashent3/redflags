"""Seed NIFTY 500 companies into database.

This script:
1. Downloads NIFTY 500 list from NSE (or loads from CSV)
2. Enriches with BSE codes and market cap data
3. Seeds companies table with all metadata

Usage:
    python scripts/seed_companies.py --source csv --file data/nifty500.csv
    python scripts/seed_companies.py --source manual --sample 50
"""

import argparse
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.models.company import Company

load_dotenv()


# Sample NIFTY 50 companies for quick testing
SAMPLE_NIFTY_50 = [
    {"name": "Reliance Industries", "nse_symbol": "RELIANCE", "bse_code": "500325", "isin": "INE002A01018", "industry": "Refineries", "sector": "Oil & Gas", "market_cap_cr": 1750000},
    {"name": "Tata Consultancy Services", "nse_symbol": "TCS", "bse_code": "532540", "isin": "INE467B01029", "industry": "IT - Software", "sector": "Technology", "market_cap_cr": 1300000},
    {"name": "HDFC Bank", "nse_symbol": "HDFCBANK", "bse_code": "500180", "isin": "INE040A01034", "industry": "Private Bank", "sector": "Banking", "market_cap_cr": 1100000},
    {"name": "Infosys", "nse_symbol": "INFY", "bse_code": "500209", "isin": "INE009A01021", "industry": "IT - Software", "sector": "Technology", "market_cap_cr": 700000},
    {"name": "ICICI Bank", "nse_symbol": "ICICIBANK", "bse_code": "532174", "isin": "INE090A01021", "industry": "Private Bank", "sector": "Banking", "market_cap_cr": 650000},
    {"name": "Bharti Airtel", "nse_symbol": "BHARTIARTL", "bse_code": "532454", "isin": "INE397D01024", "industry": "Telecom Services", "sector": "Telecommunication", "market_cap_cr": 450000},
    {"name": "State Bank of India", "nse_symbol": "SBIN", "bse_code": "500112", "isin": "INE062A01020", "industry": "Public Bank", "sector": "Banking", "market_cap_cr": 550000},
    {"name": "Hindustan Unilever", "nse_symbol": "HINDUNILVR", "bse_code": "500696", "isin": "INE030A01027", "industry": "FMCG", "sector": "Consumer Goods", "market_cap_cr": 600000},
    {"name": "ITC", "nse_symbol": "ITC", "bse_code": "500875", "isin": "INE154A01025", "industry": "Conglomerate", "sector": "Consumer Goods", "market_cap_cr": 520000},
    {"name": "Kotak Mahindra Bank", "nse_symbol": "KOTAKBANK", "bse_code": "500247", "isin": "INE237A01028", "industry": "Private Bank", "sector": "Banking", "market_cap_cr": 380000},
    {"name": "Axis Bank", "nse_symbol": "AXISBANK", "bse_code": "532215", "isin": "INE238A01034", "industry": "Private Bank", "sector": "Banking", "market_cap_cr": 340000},
    {"name": "Larsen & Toubro", "nse_symbol": "LT", "bse_code": "500510", "isin": "INE018A01030", "industry": "Infrastructure", "sector": "Construction", "market_cap_cr": 450000},
    {"name": "Asian Paints", "nse_symbol": "ASIANPAINT", "bse_code": "500820", "isin": "INE021A01026", "industry": "Paints", "sector": "Consumer Goods", "market_cap_cr": 320000},
    {"name": "Maruti Suzuki", "nse_symbol": "MARUTI", "bse_code": "532500", "isin": "INE585B01010", "industry": "Automobile", "sector": "Automobile", "market_cap_cr": 350000},
    {"name": "HCL Technologies", "nse_symbol": "HCLTECH", "bse_code": "532281", "isin": "INE860A01027", "industry": "IT - Software", "sector": "Technology", "market_cap_cr": 380000},
    {"name": "Wipro", "nse_symbol": "WIPRO", "bse_code": "507685", "isin": "INE075A01022", "industry": "IT - Software", "sector": "Technology", "market_cap_cr": 300000},
    {"name": "Bajaj Finance", "nse_symbol": "BAJFINANCE", "bse_code": "500034", "isin": "INE296A01024", "industry": "NBFC", "sector": "Banking", "market_cap_cr": 430000},
    {"name": "Mahindra & Mahindra", "nse_symbol": "M&M", "bse_code": "500520", "isin": "INE101A01026", "industry": "Automobile", "sector": "Automobile", "market_cap_cr": 250000},
    {"name": "Sun Pharmaceutical", "nse_symbol": "SUNPHARMA", "bse_code": "524715", "isin": "INE044A01036", "industry": "Pharmaceuticals", "sector": "Pharmaceuticals", "market_cap_cr": 280000},
    {"name": "Titan Company", "nse_symbol": "TITAN", "bse_code": "500114", "isin": "INE280A01028", "industry": "Retail", "sector": "Retail", "market_cap_cr": 300000},
    {"name": "UltraTech Cement", "nse_symbol": "ULTRACEMCO", "bse_code": "532538", "isin": "INE481G01011", "industry": "Cement", "sector": "Construction", "market_cap_cr": 290000},
    {"name": "Nestle India", "nse_symbol": "NESTLEIND", "bse_code": "500790", "isin": "INE239A01016", "industry": "FMCG", "sector": "Consumer Goods", "market_cap_cr": 240000},
    {"name": "Adani Enterprises", "nse_symbol": "ADANIENT", "bse_code": "512599", "isin": "INE423A01024", "industry": "Conglomerate", "sector": "Trading", "market_cap_cr": 280000},
    {"name": "Power Grid Corporation", "nse_symbol": "POWERGRID", "bse_code": "532898", "isin": "INE752E01010", "industry": "Power Transmission", "sector": "Power", "market_cap_cr": 220000},
    {"name": "NTPC", "nse_symbol": "NTPC", "bse_code": "532555", "isin": "INE733E01010", "industry": "Power Generation", "sector": "Power", "market_cap_cr": 200000},
]


def load_from_csv(file_path: str) -> pd.DataFrame:
    """Load companies from CSV file."""
    print(f"📁 Loading companies from CSV: {file_path}")

    try:
        df = pd.read_csv(file_path)
        print(f"✅ Loaded {len(df)} companies from CSV")

        # Validate required columns
        required_cols = ['name', 'nse_symbol']
        missing = [col for col in required_cols if col not in df.columns]

        if missing:
            print(f"❌ Missing required columns: {', '.join(missing)}")
            print(f"   Available columns: {', '.join(df.columns)}")
            return None

        return df

    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return None
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return None


def load_manual_sample(count: int = 50) -> pd.DataFrame:
    """Load sample companies for testing."""
    print(f"📝 Loading {min(count, len(SAMPLE_NIFTY_50))} sample companies")

    data = SAMPLE_NIFTY_50[:count]
    df = pd.DataFrame(data)

    print(f"✅ Loaded {len(df)} sample companies")
    return df


def seed_companies(df: pd.DataFrame, is_nifty_500: bool = True, dry_run: bool = False):
    """Seed companies into database."""
    db = SessionLocal()

    try:
        print("\n" + "=" * 60)
        print(f"🌱 Seeding {len(df)} companies into database")
        print("=" * 60)

        if dry_run:
            print("\n⚠️  DRY RUN MODE - No changes will be made\n")

        added = 0
        skipped = 0
        errors = 0

        for idx, row in df.iterrows():
            try:
                # Extract data
                name = row.get('name', row.get('Company Name', ''))
                nse_symbol = row.get('nse_symbol', row.get('Symbol', ''))
                bse_code = str(row.get('bse_code', '')) if pd.notna(row.get('bse_code')) else None
                isin = row.get('isin', row.get('ISIN', ''))
                industry = row.get('industry', row.get('Industry', 'Not Classified'))
                sector = row.get('sector', row.get('Sector', 'Not Classified'))
                market_cap = row.get('market_cap_cr', row.get('Market Cap', None))

                # Validate required fields
                if not name or not nse_symbol:
                    print(f"⚠️  Row {idx}: Missing name or symbol, skipping")
                    skipped += 1
                    continue

                # Check if company exists
                existing = db.query(Company).filter(
                    (Company.nse_symbol == nse_symbol) |
                    (Company.isin == isin if isin else False)
                ).first()

                if existing:
                    print(f"⏭️  {nse_symbol:<15} {name[:40]:<42} (already exists)")
                    skipped += 1
                    continue

                if not dry_run:
                    # Create company
                    company = Company(
                        name=name,
                        nse_symbol=nse_symbol,
                        bse_code=bse_code,
                        isin=isin if isin else None,
                        industry=industry,
                        sector=sector,
                        market_cap_cr=float(market_cap) if market_cap and pd.notna(market_cap) else None,
                        is_nifty_50=(idx < 50) if is_nifty_500 else False,
                        is_nifty_500=is_nifty_500,
                        is_active=True,
                    )

                    db.add(company)
                    db.flush()

                print(f"✅ {nse_symbol:<15} {name[:40]:<42} (added)")
                added += 1

                # Commit in batches of 50
                if added % 50 == 0 and not dry_run:
                    db.commit()
                    print(f"\n💾 Committed batch ({added} companies)\n")

            except IntegrityError as e:
                db.rollback()
                print(f"⚠️  {nse_symbol}: Duplicate entry, skipping")
                skipped += 1
            except Exception as e:
                db.rollback()
                print(f"❌ {nse_symbol}: Error - {e}")
                errors += 1

        # Final commit
        if not dry_run:
            db.commit()

        # Summary
        print("\n" + "=" * 60)
        print("📊 SEEDING SUMMARY")
        print("=" * 60)
        print(f"✅ Added:   {added}")
        print(f"⏭️  Skipped: {skipped}")
        print(f"❌ Errors:  {errors}")
        print(f"📈 Total:   {len(df)}")

        if dry_run:
            print("\n⚠️  This was a DRY RUN - no changes were made")

        return added

    except Exception as e:
        db.rollback()
        print(f"\n❌ Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        return 0

    finally:
        db.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Seed companies into database')
    parser.add_argument('--source', choices=['csv', 'manual'], default='manual',
                        help='Data source (csv file or manual sample)')
    parser.add_argument('--file', type=str, help='Path to CSV file (if source=csv)')
    parser.add_argument('--sample', type=int, default=25,
                        help='Number of sample companies to load (if source=manual)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Run without making changes to database')

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("🌱 Company Seeding Script")
    print("=" * 60)

    # Load data
    if args.source == 'csv':
        if not args.file:
            print("❌ Please specify --file when using --source csv")
            return 1

        df = load_from_csv(args.file)
        if df is None:
            return 1

    else:  # manual
        df = load_manual_sample(args.sample)

    # Seed companies
    added = seed_companies(df, is_nifty_500=True, dry_run=args.dry_run)

    if added > 0 or args.dry_run:
        print("\n✅ Seeding completed successfully!")
        print("\nNext steps:")
        print("   1. Verify companies: SELECT COUNT(*) FROM companies;")
        print("   2. Seed annual reports: python scripts/seed_annual_reports.py")
        return 0
    else:
        print("\n⚠️  No companies were added")
        return 1


if __name__ == "__main__":
    sys.exit(main())
