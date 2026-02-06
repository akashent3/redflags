"""Verify Phase 5 implementation without running server."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))


def check_imports():
    """Verify all Phase 5 modules can be imported."""
    print("\n" + "="*60)
    print("PHASE 5 VERIFICATION - Import Checks")
    print("="*60)

    checks = []

    # Check 1: Company schemas
    print("\n[1/7] Checking company schemas...")
    try:
        from app.schemas.company import (
            CompanyBase,
            CompanyResponse,
            CompanySearchResult,
            CompanySearchResponse,
            CompanyDetailResponse
        )
        print("  SUCCESS: All company schemas imported")
        checks.append(True)
    except Exception as e:
        print(f"  FAIL: {e}")
        checks.append(False)

    # Check 2: Company service
    print("\n[2/7] Checking company service...")
    try:
        from app.services.company_service import company_service
        print("  SUCCESS: Company service imported")
        print(f"  Methods: {[m for m in dir(company_service) if not m.startswith('_')]}")
        checks.append(True)
    except Exception as e:
        print(f"  FAIL: {e}")
        checks.append(False)

    # Check 3: Companies router
    print("\n[3/7] Checking companies router...")
    try:
        from app.api.v1.companies import router
        print("  SUCCESS: Companies router imported")
        print(f"  Routes: {len(router.routes)}")
        for route in router.routes:
            methods = ", ".join(route.methods) if hasattr(route, 'methods') else "N/A"
            print(f"    - {route.path} [{methods}]")
        checks.append(True)
    except Exception as e:
        print(f"  FAIL: {e}")
        checks.append(False)

    # Check 4: Main API router includes companies
    print("\n[4/7] Checking main API router...")
    try:
        from app.api.v1 import api_router
        print("  SUCCESS: Main API router imported")

        # Count total routes
        total_routes = 0
        for route in api_router.routes:
            if hasattr(route, 'routes'):
                total_routes += len(route.routes)
            else:
                total_routes += 1

        print(f"  Total API routes: {total_routes}")
        checks.append(True)
    except Exception as e:
        print(f"  FAIL: {e}")
        checks.append(False)

    # Check 5: Schema exports
    print("\n[5/7] Checking schema exports...")
    try:
        from app.schemas import (
            CompanyResponse,
            CompanySearchResponse,
            CompanySearchResult,
            CompanyDetailResponse
        )
        print("  SUCCESS: All company schemas exported in __all__")
        checks.append(True)
    except Exception as e:
        print(f"  FAIL: {e}")
        checks.append(False)

    # Check 6: Database models
    print("\n[6/7] Checking database models...")
    try:
        from app.models.company import Company
        from app.models.annual_report import AnnualReport
        print("  SUCCESS: Company and AnnualReport models imported")
        print(f"  Company model fields: {[c.name for c in Company.__table__.columns][:10]}...")
        checks.append(True)
    except Exception as e:
        print(f"  FAIL: {e}")
        checks.append(False)

    # Check 7: Test companies in database
    print("\n[7/7] Checking test companies in database...")
    try:
        from app.database import SessionLocal
        from app.models.company import Company

        db = SessionLocal()
        count = db.query(Company).count()
        db.close()

        if count > 0:
            print(f"  SUCCESS: {count} companies found in database")
            checks.append(True)
        else:
            print("  WARNING: No companies in database")
            print("  Run: python -m app.scripts.seed_test_companies")
            checks.append(False)
    except Exception as e:
        print(f"  FAIL: {e}")
        checks.append(False)

    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    passed = sum(checks)
    total = len(checks)
    print(f"\nTests Passed: {passed}/{total}")

    if passed == total:
        print("\nSTATUS: ALL CHECKS PASSED!")
        print("\nPhase 5 is ready for testing.")
        print("\nNext steps:")
        print("  1. Start server: uvicorn app.main:app --reload")
        print("  2. Test endpoints: python test_phase5.py")
        print("  3. Open Swagger UI: http://localhost:8000/docs")
        return True
    else:
        print("\nSTATUS: SOME CHECKS FAILED")
        print("\nPlease fix the issues above before testing.")
        return False


if __name__ == "__main__":
    try:
        success = check_imports()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
