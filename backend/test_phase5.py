"""Quick test script for Phase 5 company endpoints."""

import requests
import json
from time import sleep

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

# Test credentials (update with actual test user)
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpass123"


def print_result(title, response):
    """Pretty print test results."""
    print(f"\n{'='*60}")
    print(f"TEST: {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")

    try:
        data = response.json()
        print(f"Response:\n{json.dumps(data, indent=2)}")
    except:
        print(f"Response: {response.text[:200]}")

    if response.status_code in [200, 201]:
        print("RESULT: PASS")
    else:
        print("RESULT: FAIL")
    return response


def main():
    """Run Phase 5 tests."""
    print("\n" + "="*60)
    print("PHASE 5 TESTING - Company Search Endpoints")
    print("="*60)

    # Step 1: Create test user (if doesn't exist)
    print("\n[1/6] Creating test user...")
    signup_response = requests.post(
        f"{API_URL}/auth/signup",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "full_name": "Test User"
        }
    )

    if signup_response.status_code == 400:
        print("User already exists (OK)")
    elif signup_response.status_code == 201:
        print("User created successfully")
    else:
        print(f"Unexpected response: {signup_response.status_code}")

    # Step 2: Login and get token
    print("\n[2/6] Logging in...")
    login_response = requests.post(
        f"{API_URL}/auth/login",
        data={
            "username": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
    )

    if login_response.status_code != 200:
        print("ERROR: Login failed!")
        print(login_response.json())
        return

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"Login successful! Token: {token[:20]}...")

    # Step 3: Test Company Search
    print("\n[3/6] Testing: GET /api/v1/companies/search")

    # Test 3a: Search by name
    print_result(
        "Search by name (reliance)",
        requests.get(
            f"{API_URL}/companies/search",
            params={"q": "reliance"},
            headers=headers
        )
    )

    # Test 3b: Search by NSE symbol
    print_result(
        "Search by NSE symbol (TCS)",
        requests.get(
            f"{API_URL}/companies/search",
            params={"q": "TCS"},
            headers=headers
        )
    )

    # Test 3c: Search partial (bank)
    search_response = print_result(
        "Search partial name (bank)",
        requests.get(
            f"{API_URL}/companies/search",
            params={"q": "bank", "limit": 3},
            headers=headers
        )
    )

    # Save a company_id for next tests
    company_id = None
    if search_response.status_code == 200:
        results = search_response.json().get("results", [])
        if results:
            company_id = results[0]["id"]
            print(f"\nUsing company_id for next tests: {company_id}")

    if not company_id:
        print("\nERROR: No companies found! Cannot continue tests.")
        return

    # Step 4: Test Get Company Details
    print(f"\n[4/6] Testing: GET /api/v1/companies/{company_id}")
    company_detail = print_result(
        "Get company details",
        requests.get(
            f"{API_URL}/companies/{company_id}",
            headers=headers
        )
    )

    # Step 5: Test Get Company Reports
    print(f"\n[5/6] Testing: GET /api/v1/companies/{company_id}/reports")
    print_result(
        "Get company reports (should be empty initially)",
        requests.get(
            f"{API_URL}/companies/{company_id}/reports",
            headers=headers
        )
    )

    # Step 6: Test NIFTY 500 filter
    print("\n[6/6] Testing: Search with NIFTY 500 filter")
    print_result(
        "Search with nifty_500_only=true",
        requests.get(
            f"{API_URL}/companies/search",
            params={"q": "bank", "nifty_500_only": True},
            headers=headers
        )
    )

    # Summary
    print("\n" + "="*60)
    print("PHASE 5 TESTING COMPLETE")
    print("="*60)
    print("\nAll 3 endpoints tested:")
    print("  1. GET /api/v1/companies/search - Company search")
    print("  2. GET /api/v1/companies/{id} - Company details")
    print("  3. GET /api/v1/companies/{id}/reports - Company reports")
    print("\nCheck results above for PASS/FAIL status.")
    print("\nNext: Open http://localhost:8000/docs to test in Swagger UI")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\nERROR: Cannot connect to server!")
        print("Please start the server first:")
        print("  cd D:/redflags/backend")
        print("  uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
