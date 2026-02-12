"""
Seed script to add Reliance Industries and its annual reports to the database.
This allows testing the company search → analysis workflow.

Run this script to:
1. Create Reliance Industries company record
2. Create AnnualReport records for the 3 PDFs in data/pdfs/
3. Enable testing of the full workflow

Usage:
    python -m app.scripts.seed_reliance
"""

import os
import sys
from pathlib import Path
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.company import Company
from app.models.annual_report import AnnualReport


def seed_reliance_data():
    """Seed Reliance Industries company and annual reports."""
    
    db: Session = SessionLocal()
    
    try:
        print("🚀 Starting Reliance data seeding...")
        
        # Check if Reliance already exists
        existing_company = db.query(Company).filter(
            Company.nse_symbol == "RELIANCE"
        ).first()
        
        if existing_company:
            print(f"✅ Reliance Industries already exists (ID: {existing_company.id})")
            company = existing_company
        else:
            # Create Reliance Industries company
            company = Company(
                id=uuid4(),
                name="Reliance Industries Ltd",
                bse_code="500325",
                nse_symbol="RELIANCE",
                isin="INE002A01018",
                industry="Oil & Gas",
                sector="Energy",
                market_cap_cr=1750000.00,  # ~17.5 lakh crores
                is_nifty_50=True,
                is_nifty_500=True,
                is_active=True
            )
            
            db.add(company)
            db.commit()
            db.refresh(company)
            
            print(f"✅ Created Reliance Industries (ID: {company.id})")
        
        # Define the PDFs
        pdf_dir = Path(__file__).parent.parent.parent / "data" / "pdfs"
        
        pdfs = [
            {
                "filename": "RELIANCE_AR_2023.pdf",
                "fiscal_year": "2022-23",
                "file_size_mb": 16.53
            },
            {
                "filename": "RELIANCE_AR_2024.pdf",
                "fiscal_year": "2023-24",
                "file_size_mb": 12.35
            },
            {
                "filename": "RELIANCE_AR_2025.pdf",
                "fiscal_year": "2024-25",
                "file_size_mb": 8.86
            }
        ]
        
        reports_created = 0
        reports_skipped = 0
        
        for pdf_info in pdfs:
            # Check if report already exists
            existing_report = db.query(AnnualReport).filter(
                AnnualReport.company_id == company.id,
                AnnualReport.fiscal_year == pdf_info["fiscal_year"]
            ).first()
            
            if existing_report:
                print(f"⏭️  Report {pdf_info['fiscal_year']} already exists, skipping...")
                reports_skipped += 1
                continue
            
            # Check if PDF file exists
            pdf_path = pdf_dir / pdf_info["filename"]
            if not pdf_path.exists():
                print(f"⚠️  PDF file not found: {pdf_path}")
                continue
            
            # Create annual report record
            # For local development, we'll use file:// URL
            # In production, this would be an R2 URL
            report = AnnualReport(
                id=uuid4(),
                company_id=company.id,
                fiscal_year=pdf_info["fiscal_year"],
                pdf_url=f"file://{pdf_path.absolute()}",  # Local file path
                file_size_mb=pdf_info["file_size_mb"],
                pages_count=None,  # Will be set during analysis
                is_processed="not_started",
                uploaded_at=None
            )
            
            db.add(report)
            reports_created += 1
            
            print(f"✅ Created report: {pdf_info['fiscal_year']} (ID: {report.id})")
        
        db.commit()
        
        print("\n" + "="*60)
        print("🎉 Seeding completed successfully!")
        print("="*60)
        print(f"Company: {company.name} ({company.nse_symbol})")
        print(f"Company ID: {company.id}")
        print(f"Reports created: {reports_created}")
        print(f"Reports skipped: {reports_skipped}")
        print("\n📝 Next steps:")
        print("1. Start the backend: uvicorn app.main:app --reload")
        print("2. Start Celery worker: celery -A app.celery_app worker --loglevel=info --pool=solo")
        print("3. Test company search: GET /api/v1/companies/search?q=reliance")
        print("4. Get company reports: GET /api/v1/companies/{company_id}/reports")
        print("5. Trigger analysis: POST /api/v1/analysis/analyze/{report_id}")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    seed_reliance_data()
