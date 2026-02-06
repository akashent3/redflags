"""Seed script to add test companies for development."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.database import SessionLocal
from app.models.company import Company


def seed_test_companies():
    """Add test companies to database."""
    db = SessionLocal()

    try:
        # Check if companies already exist
        existing = db.query(Company).count()
        if existing > 0:
            print(f"Database already has {existing} companies. Skipping seed.")
            return

        # Sample companies for testing
        test_companies = [
            {
                "name": "Reliance Industries Limited",
                "nse_symbol": "RELIANCE",
                "bse_code": "500325",
                "isin": "INE002A01018",
                "industry": "Refinery",
                "sector": "Oil & Gas",
                "market_cap_cr": 1758000.00,
                "is_nifty_50": True,
                "is_nifty_500": True,
            },
            {
                "name": "Tata Consultancy Services Limited",
                "nse_symbol": "TCS",
                "bse_code": "532540",
                "isin": "INE467B01029",
                "industry": "IT Services & Consulting",
                "sector": "Information Technology",
                "market_cap_cr": 1275000.00,
                "is_nifty_50": True,
                "is_nifty_500": True,
            },
            {
                "name": "HDFC Bank Limited",
                "nse_symbol": "HDFCBANK",
                "bse_code": "500180",
                "isin": "INE040A01034",
                "industry": "Private Bank",
                "sector": "Financial Services",
                "market_cap_cr": 1145000.00,
                "is_nifty_50": True,
                "is_nifty_500": True,
            },
            {
                "name": "Infosys Limited",
                "nse_symbol": "INFY",
                "bse_code": "500209",
                "isin": "INE009A01021",
                "industry": "IT Services & Consulting",
                "sector": "Information Technology",
                "market_cap_cr": 642000.00,
                "is_nifty_50": True,
                "is_nifty_500": True,
            },
            {
                "name": "ICICI Bank Limited",
                "nse_symbol": "ICICIBANK",
                "bse_code": "532174",
                "isin": "INE090A01021",
                "industry": "Private Bank",
                "sector": "Financial Services",
                "market_cap_cr": 782000.00,
                "is_nifty_50": True,
                "is_nifty_500": True,
            },
            {
                "name": "Hindustan Unilever Limited",
                "nse_symbol": "HINDUNILVR",
                "bse_code": "500696",
                "isin": "INE030A01027",
                "industry": "FMCG",
                "sector": "Consumer Goods",
                "market_cap_cr": 589000.00,
                "is_nifty_50": True,
                "is_nifty_500": True,
            },
            {
                "name": "State Bank of India",
                "nse_symbol": "SBIN",
                "bse_code": "500112",
                "isin": "INE062A01020",
                "industry": "Public Bank",
                "sector": "Financial Services",
                "market_cap_cr": 662000.00,
                "is_nifty_50": True,
                "is_nifty_500": True,
            },
            {
                "name": "Bharti Airtel Limited",
                "nse_symbol": "BHARTIARTL",
                "bse_code": "532454",
                "isin": "INE397D01024",
                "industry": "Telecom Services",
                "sector": "Telecommunication",
                "market_cap_cr": 465000.00,
                "is_nifty_50": True,
                "is_nifty_500": True,
            },
            {
                "name": "ITC Limited",
                "nse_symbol": "ITC",
                "bse_code": "500125",
                "isin": "INE154A01025",
                "industry": "Diversified FMCG",
                "sector": "Consumer Goods",
                "market_cap_cr": 512000.00,
                "is_nifty_50": True,
                "is_nifty_500": True,
            },
            {
                "name": "Kotak Mahindra Bank Limited",
                "nse_symbol": "KOTAKBANK",
                "bse_code": "500247",
                "isin": "INE237A01028",
                "industry": "Private Bank",
                "sector": "Financial Services",
                "market_cap_cr": 365000.00,
                "is_nifty_50": True,
                "is_nifty_500": True,
            },
            # Add a few non-NIFTY 50 companies
            {
                "name": "Yes Bank Limited",
                "nse_symbol": "YESBANK",
                "bse_code": "532648",
                "isin": "INE528G01035",
                "industry": "Private Bank",
                "sector": "Financial Services",
                "market_cap_cr": 6500.00,
                "is_nifty_50": False,
                "is_nifty_500": True,
            },
            {
                "name": "Zee Entertainment Enterprises Limited",
                "nse_symbol": "ZEEL",
                "bse_code": "505537",
                "isin": "INE256A01028",
                "industry": "Media & Entertainment",
                "sector": "Media",
                "market_cap_cr": 12500.00,
                "is_nifty_50": False,
                "is_nifty_500": True,
            },
        ]

        # Add companies to database
        for company_data in test_companies:
            company = Company(**company_data)
            db.add(company)

        db.commit()
        print(f"Successfully seeded {len(test_companies)} test companies!")

        # Print summary
        print("\nCompanies added:")
        for company_data in test_companies:
            nifty = "NIFTY 50" if company_data["is_nifty_50"] else "NIFTY 500"
            print(f"  - {company_data['name']} ({company_data['nse_symbol']}) - {nifty}")

    except Exception as e:
        print(f"Error seeding companies: {e}")
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    print("Seeding test companies...")
    seed_test_companies()
    print("\nDone!")
