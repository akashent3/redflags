"""Update R2 URLs from pub-xxx.r2.dev to custom domain."""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.database import SessionLocal
from app.models.annual_report import AnnualReport
from dotenv import load_dotenv

load_dotenv()

def update_r2_urls():
    """Replace old R2 URLs with custom domain URLs."""
    
    # Get custom domain from .env
    custom_domain = os.getenv('R2_PUBLIC_URL')
    
    if not custom_domain:
        print("❌ R2_PUBLIC_URL not set in .env file")
        return False
    
    # Remove trailing slash
    custom_domain = custom_domain.rstrip('/')
    
    # Add https:// if not present
    if not custom_domain.startswith('http'):
        custom_domain = f"https://{custom_domain}"
    
    print("\n" + "=" * 60)
    print("🔄 Updating R2 URLs to Custom Domain")
    print("=" * 60)
    print(f"Custom Domain: {custom_domain}\n")
    
    db = SessionLocal()
    
    try:
        # Find all reports with old R2 URLs
        old_pattern = 'https://pub-%'
        reports = db.query(AnnualReport).filter(
            AnnualReport.pdf_url.like(old_pattern)
        ).all()
        
        if not reports:
            print("✅ No reports found with old R2 URLs")
            return True
        
        print(f"📊 Found {len(reports)} reports to update\n")
        
        updated_count = 0
        
        for report in reports:
            old_url = report.pdf_url
            
            # Extract the path after .r2.dev/
            if '.r2.dev/' in old_url:
                path = old_url.split('.r2.dev/')[-1]
                new_url = f"{custom_domain}/{path}"
                
                # Update the URL
                report.pdf_url = new_url
                updated_count += 1
                
                # Convert UUID to string for printing
                report_id_str = str(report.id)[:8]
                
                print(f"✓ Updated report {report_id_str}...")
                print(f"  Old: {old_url[:80]}...")
                print(f"  New: {new_url[:80]}...\n")
        
        # Commit changes
        if updated_count > 0:
            print("💾 Committing changes to database...")
            db.commit()
            print("\n" + "=" * 60)
            print(f"✅ Successfully updated {updated_count} report URLs")
            print("=" * 60)
            print("\n⚠️  IMPORTANT: Restart your backend and Celery worker:")
            print("   • Backend: uvicorn app.main:app --reload")
            print("   • Celery: celery -A app.celery_app worker --loglevel=info --pool=solo")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()


if __name__ == "__main__":
    success = update_r2_urls()
    sys.exit(0 if success else 1)