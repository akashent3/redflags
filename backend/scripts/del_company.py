"""
Standalone script to delete all analysis data AND reports for a company by NSE symbol.

Usage:
    python delete_company_analysis.py RELIANCE
    python delete_company_analysis.py ITC --force
    python delete_company_analysis.py TCS --keep-reports  # Keep reports, only delete analysis
"""

import sys
import os
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.company import Company
from app.models.annual_report import AnnualReport
from app.models.analysis_result import AnalysisResult
from app.models.red_flag import RedFlag
from app.models.user_analysis import UserAnalysis


def delete_company_analysis(symbol: str, force: bool = False, keep_reports: bool = False):
    """
    Delete ALL analysis data for a company by NSE symbol.
    
    This will delete:
    - Analysis results
    - Red flags
    - User analysis tracking records
    - Annual reports (COMPLETELY DELETED by default, or reset to 'pending' if --keep-reports)
    
    Args:
        symbol: NSE stock symbol (e.g., 'RELIANCE', 'ITC')
        force: If True, skip confirmation prompt
        keep_reports: If True, keep report records and just reset to 'pending'
                     If False (default), completely delete all report records
    """
    # Create database connection
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Step 1: Find company by symbol
        print(f"\n🔍 Searching for company: {symbol}")
        company = db.query(Company).filter(Company.nse_symbol == symbol.upper()).first()
        
        if not company:
            print(f"❌ Company with symbol '{symbol}' not found in database.")
            print(f"\nAvailable companies:")
            companies = db.query(Company.name, Company.nse_symbol).limit(10).all()
            for c_name, c_symbol in companies:
                print(f"  - {c_symbol}: {c_name}")
            return False
        
        print(f"✅ Found: {company.name} ({company.nse_symbol})")
        print(f"   Company ID: {company.id}")
        
        # Step 2: Get all reports for this company
        reports = db.query(AnnualReport).filter(AnnualReport.company_id == company.id).all()
        
        if not reports:
            print(f"\n⚠️  No reports found for {company.name}")
            return True
        
        print(f"\n📊 Found {len(reports)} report(s):")
        
        # Step 3: Count what will be deleted
        total_analyses = 0
        total_flags = 0
        total_user_analyses = 0
        
        report_details = []
        
        for report in reports:
            # Count analyses
            analyses = db.query(AnalysisResult).filter(AnalysisResult.report_id == report.id).all()
            
            analysis_count_for_report = len(analyses)
            flag_count_for_report = 0
            user_analysis_count_for_report = 0
            
            for analysis in analyses:
                # Count flags
                flag_count = db.query(RedFlag).filter(RedFlag.analysis_id == analysis.id).count()
                
                # Count user analyses
                user_analysis_count = db.query(UserAnalysis).filter(UserAnalysis.analysis_id == analysis.id).count()
                
                total_analyses += 1
                total_flags += flag_count
                total_user_analyses += user_analysis_count
                
                flag_count_for_report += flag_count
                user_analysis_count_for_report += user_analysis_count
            
            report_details.append({
                'fiscal_year': report.fiscal_year,
                'report_id': report.id,
                'analysis_count': analysis_count_for_report,
                'flags': flag_count_for_report,
                'user_analyses': user_analysis_count_for_report,
                'status': report.is_processed,
                'pdf_url': report.pdf_url
            })
        
        # Display summary
        print(f"\n📋 DELETION SUMMARY:")
        print(f"   Company: {company.name} ({company.nse_symbol})")
        print(f"   Reports: {len(reports)}")
        print(f"   Analyses: {total_analyses}")
        print(f"   Red Flags: {total_flags}")
        print(f"   User Analysis Records: {total_user_analyses}")
        
        print(f"\n📄 REPORT DETAILS:")
        for detail in report_details:
            status_emoji = "✅" if detail['status'] == 'completed' else "⏳" if detail['status'] == 'pending' else "❌"
            analysis_info = f"{detail['analysis_count']} analysis, {detail['flags']} flags" if detail['analysis_count'] > 0 else "No analysis"
            print(f"   {status_emoji} FY {detail['fiscal_year']}: {analysis_info} - Status: {detail['status']}")
        
        # Confirmation prompt
        if not force:
            print(f"\n⚠️  WARNING: This will permanently delete:")
            print(f"   • {total_analyses} analysis result(s)")
            print(f"   • {total_flags} red flag record(s)")
            print(f"   • {total_user_analyses} user analysis tracking record(s)")
            
            if keep_reports:
                print(f"   • Reports will be reset to 'pending' status (kept in database)")
            else:
                print(f"   • {len(reports)} annual report record(s) will be COMPLETELY DELETED")
                print(f"   • This includes ALL reports (completed, pending, failed)")
            
            confirm = input(f"\n❓ Delete ALL data for {company.name}? Type 'yes' to confirm: ")
            
            if confirm.lower() != 'yes':
                print("❌ Deletion cancelled.")
                return False
        
        # Step 4: Perform deletion
        print(f"\n🗑️  Deleting data...")
        
        deleted_analyses = 0
        deleted_flags = 0
        deleted_user_analyses = 0
        deleted_reports = 0
        reset_reports = 0
        
        for report in reports:
            # Get all analyses for this report
            analyses = db.query(AnalysisResult).filter(AnalysisResult.report_id == report.id).all()
            
            for analysis in analyses:
                # Delete user_analyses records (must delete first due to foreign key)
                user_analysis_records = db.query(UserAnalysis).filter(UserAnalysis.analysis_id == analysis.id).all()
                for ua in user_analysis_records:
                    db.delete(ua)
                    deleted_user_analyses += 1
                
                # Delete red flags
                flags = db.query(RedFlag).filter(RedFlag.analysis_id == analysis.id).all()
                for flag in flags:
                    db.delete(flag)
                    deleted_flags += 1
                
                # Delete analysis result
                db.delete(analysis)
                deleted_analyses += 1
            
            # Handle report deletion or reset
            if keep_reports:
                # Reset report status to pending
                report.is_processed = 'pending'
                report.processed_at = None
                reset_reports += 1
            else:
                # Completely delete the report record
                db.delete(report)
                deleted_reports += 1
        
        # Commit all changes
        db.commit()
        
        print(f"\n✅ DELETION COMPLETE:")
        print(f"   ✓ Deleted {deleted_analyses} analysis result(s)")
        print(f"   ✓ Deleted {deleted_flags} red flag(s)")
        print(f"   ✓ Deleted {deleted_user_analyses} user analysis record(s)")
        
        if keep_reports:
            print(f"   ✓ Reset {reset_reports} report(s) to 'pending' status")
        else:
            print(f"   ✓ Deleted {deleted_reports} annual report record(s) COMPLETELY")
        
        print(f"\n🎉 All data for {company.name} has been deleted!")
        
        if keep_reports:
            print(f"   You can now re-analyze this company to create fresh analysis.")
        else:
            print(f"   All reports have been removed. You'll need to re-fetch reports before analyzing.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Delete all analysis data and reports for a company by NSE symbol',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Delete everything (analysis + reports)
  python delete_company_analysis.py RELIANCE
  
  # Delete everything without confirmation
  python delete_company_analysis.py ITC --force
  
  # Keep reports, only delete analysis (reset to pending)
  python delete_company_analysis.py TCS --keep-reports

By default, this script will delete:
  • All analysis results
  • All red flags
  • All user analysis tracking records
  • All annual report records (including pending/failed ones)

Use --keep-reports to preserve report records and just reset to 'pending'
        """
    )
    
    parser.add_argument(
        'symbol',
        type=str,
        help='NSE stock symbol (e.g., RELIANCE, ITC, TCS)'
    )
    
    parser.add_argument(
        '-f', '--force',
        action='store_true',
        help='Skip confirmation prompt'
    )
    
    parser.add_argument(
        '--keep-reports',
        action='store_true',
        help='Keep report records, only delete analysis data and reset to pending'
    )
    
    args = parser.parse_args()
    
    # Run deletion
    success = delete_company_analysis(args.symbol, args.force, args.keep_reports)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()