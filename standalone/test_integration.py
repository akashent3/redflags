#!/usr/bin/env python3
"""Integration test for standalone app."""

import sys
import time
import requests

def test_health_check():
    """Test health endpoint."""
    print("Testing health endpoint...")
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Health check passed: {data['status']}")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

def test_invalid_filename():
    """Test invalid filename format."""
    print("\nTesting invalid filename...")
    try:
        # Create a dummy PDF content
        pdf_content = b"%PDF-1.4\n%test content"
        files = {'file': ('invalid.pdf', pdf_content, 'application/pdf')}
        
        response = requests.post("http://localhost:8000/api/upload", files=files, timeout=5)
        
        if response.status_code == 400:
            print(f"✓ Invalid filename rejected correctly")
            return True
        else:
            print(f"✗ Expected 400, got {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_invalid_symbol():
    """Test invalid stock symbol."""
    print("\nTesting invalid stock symbol...")
    try:
        pdf_content = b"%PDF-1.4\n%test content"
        files = {'file': ('INVALID_2025.pdf', pdf_content, 'application/pdf')}
        
        response = requests.post("http://localhost:8000/api/upload", files=files, timeout=5)
        
        if response.status_code == 400 and 'symbol' in response.text.lower():
            print(f"✓ Invalid symbol rejected correctly")
            return True
        else:
            print(f"✗ Expected 400 with symbol error, got {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Standalone App Integration Tests")
    print("=" * 60)
    print("\nMake sure the server is running on http://localhost:8000")
    print("Start with: cd standalone/backend && python app.py")
    print("\n" + "=" * 60)
    
    time.sleep(2)
    
    results = []
    results.append(("Health Check", test_health_check()))
    results.append(("Invalid Filename", test_invalid_filename()))
    results.append(("Invalid Symbol", test_invalid_symbol()))
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(passed for _, passed in results)
    print("\n" + "=" * 60)
    if all_passed:
        print("All tests passed! ✓")
        return 0
    else:
        print("Some tests failed! ✗")
        return 1

if __name__ == "__main__":
    sys.exit(main())
