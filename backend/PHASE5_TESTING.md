# Phase 5 - Company Search Endpoints - Testing Guide

## Overview

Phase 5 has been completed with the implementation of 3 new company search endpoints. This document provides instructions for testing the new functionality.

## Files Created

### 1. Schemas (`app/schemas/company.py`)
- `CompanyBase` - Base company schema
- `CompanyResponse` - Basic company response
- `CompanySearchResult` - Single search result
- `CompanySearchResponse` - Search results list
- `CompanyDetailResponse` - Detailed company info with stats

### 2. Service (`app/services/company_service.py`)
- `search_companies()` - Search by name, NSE symbol, or BSE code
- `get_company_by_id()` - Get company details
- `get_company_reports()` - Get company's annual reports
- `get_company_report_stats()` - Get report statistics

### 3. API Router (`app/api/v1/companies.py`)
Three new endpoints:
- `GET /api/v1/companies/search` - Search companies
- `GET /api/v1/companies/{company_id}` - Get company details
- `GET /api/v1/companies/{company_id}/reports` - Get company reports

### 4. Updated Files
- `app/schemas/__init__.py` - Added company schema exports
- `app/api/v1/__init__.py` - Registered companies router

### 5. Test Data Script
- `app/scripts/seed_test_companies.py` - Seeds 12 test companies

---

## Setup Instructions

### 1. Activate Virtual Environment
```bash
cd D:\redflags\backend
.\venv\Scripts\activate
```

### 2. Seed Test Companies
```bash
python -m app.scripts.seed_test_companies
```

This will add 12 test companies:
- **NIFTY 50 (10 companies)**: Reliance, TCS, HDFC Bank, Infosys, ICICI Bank, HUL, SBI, Bharti Airtel, ITC, Kotak Bank
- **NIFTY 500 only (2 companies)**: Yes Bank, Zee Entertainment

### 3. Start the FastAPI Server
```bash
uvicorn app.main:app --reload
```

### 4. Access Swagger UI
Open browser: http://localhost:8000/docs

---

## API Testing

### Endpoint 1: Search Companies

**URL**: `GET /api/v1/companies/search`

**Authentication**: Required (JWT token)

**Query Parameters**:
- `q` (required): Search query (name, NSE symbol, or BSE code)
- `limit` (optional): Max results (1-100, default 20)
- `nifty_500_only` (optional): Filter to NIFTY 500 only (default false)

**Test Cases**:

1. **Search by company name**:
   ```
   GET /api/v1/companies/search?q=reliance
   ```
   Expected: Returns Reliance Industries

2. **Search by NSE symbol**:
   ```
   GET /api/v1/companies/search?q=TCS
   ```
   Expected: Returns Tata Consultancy Services

3. **Search by partial name**:
   ```
   GET /api/v1/companies/search?q=bank
   ```
   Expected: Returns HDFC Bank, ICICI Bank, SBI, Kotak Bank, Yes Bank

4. **Search with NIFTY 500 filter**:
   ```
   GET /api/v1/companies/search?q=bank&nifty_500_only=true
   ```
   Expected: Returns all banks (all are in NIFTY 500)

5. **Search with limit**:
   ```
   GET /api/v1/companies/search?q=bank&limit=2
   ```
   Expected: Returns first 2 banks only

**Expected Response**:
```json
{
  "total": 5,
  "results": [
    {
      "id": "uuid-here",
      "name": "HDFC Bank Limited",
      "display_code": "HDFCBANK",
      "industry": "Private Bank",
      "sector": "Financial Services",
      "is_nifty_50": true,
      "is_nifty_500": true,
      "market_cap_cr": 1145000.00
    },
    ...
  ]
}
```

---

### Endpoint 2: Get Company Details

**URL**: `GET /api/v1/companies/{company_id}`

**Authentication**: Required (JWT token)

**Path Parameters**:
- `company_id` (required): Company UUID

**Test Cases**:

1. **Get valid company**:
   - First, search for a company to get its UUID
   - Then use that UUID: `GET /api/v1/companies/{uuid}`

2. **Get non-existent company**:
   - Use invalid UUID: `GET /api/v1/companies/00000000-0000-0000-0000-000000000000`
   - Expected: 404 Not Found error

**Expected Response**:
```json
{
  "id": "uuid-here",
  "name": "Reliance Industries Limited",
  "bse_code": "500325",
  "nse_symbol": "RELIANCE",
  "isin": "INE002A01018",
  "industry": "Refinery",
  "sector": "Oil & Gas",
  "market_cap_cr": 1758000.00,
  "is_nifty_50": true,
  "is_nifty_500": true,
  "is_active": true,
  "display_code": "RELIANCE",
  "is_nifty": true,
  "created_at": "2026-02-06T10:30:00Z",
  "updated_at": null,
  "total_reports": 0,
  "latest_report_year": null,
  "earliest_report_year": null
}
```

---

### Endpoint 3: Get Company Reports

**URL**: `GET /api/v1/companies/{company_id}/reports`

**Authentication**: Required (JWT token)

**Path Parameters**:
- `company_id` (required): Company UUID

**Query Parameters**:
- `skip` (optional): Records to skip (default 0)
- `limit` (optional): Max results (1-100, default 20)

**Test Cases**:

1. **Get reports for company**:
   ```
   GET /api/v1/companies/{company_id}/reports
   ```
   Expected: Empty list initially (no reports uploaded yet)

2. **After uploading a report**:
   - Upload an annual report for a company via `POST /api/v1/reports/upload`
   - Then fetch reports: `GET /api/v1/companies/{company_id}/reports`
   - Expected: List with uploaded report

3. **Pagination test**:
   ```
   GET /api/v1/companies/{company_id}/reports?skip=0&limit=10
   ```

4. **Invalid company**:
   ```
   GET /api/v1/companies/00000000-0000-0000-0000-000000000000/reports
   ```
   Expected: 404 Not Found error

**Expected Response**:
```json
{
  "total": 1,
  "skip": 0,
  "limit": 20,
  "reports": [
    {
      "id": "report-uuid",
      "company_id": "company-uuid",
      "fiscal_year": 2023,
      "fiscal_year_display": "FY2023-24",
      "pdf_url": "https://r2.example.com/...",
      "file_size_mb": 2.5,
      "pages_count": 150,
      "is_processed": "completed",
      "uploaded_at": "2026-02-06T10:30:00Z",
      "processed_at": "2026-02-06T10:35:00Z"
    }
  ]
}
```

---

## Integration Testing Workflow

### Complete End-to-End Test:

1. **Signup/Login**:
   ```
   POST /api/v1/auth/signup
   POST /api/v1/auth/login
   ```
   Save JWT token

2. **Search for a company**:
   ```
   GET /api/v1/companies/search?q=TCS
   ```
   Save company_id from response

3. **Get company details**:
   ```
   GET /api/v1/companies/{company_id}
   ```
   Verify: total_reports = 0 initially

4. **Upload annual report for this company**:
   ```
   POST /api/v1/reports/upload
   ```
   Include company_name="Tata Consultancy Services Limited", fiscal_year=2023

5. **Get company reports**:
   ```
   GET /api/v1/companies/{company_id}/reports
   ```
   Verify: List now shows 1 report

6. **Trigger analysis**:
   ```
   POST /api/v1/analysis/analyze/{report_id}
   ```
   Get task_id

7. **Check analysis status**:
   ```
   GET /api/v1/analysis/task/{task_id}
   ```
   Poll until status = SUCCESS

8. **View analysis results**:
   ```
   GET /api/v1/analysis/{analysis_id}
   ```

---

## Swagger UI Testing Steps

1. **Open Swagger UI**: http://localhost:8000/docs

2. **Authorize**:
   - Click "Authorize" button (lock icon)
   - Login to get JWT token
   - Enter token as: `Bearer <your-token>`
   - Click "Authorize"

3. **Test Companies Endpoints**:
   - Expand "Companies" section
   - Try each endpoint:
     - `/api/v1/companies/search`
     - `/api/v1/companies/{company_id}`
     - `/api/v1/companies/{company_id}/reports`

4. **Verify Responses**:
   - Check response status (200 OK)
   - Verify response schema matches documentation
   - Check data accuracy

---

## Expected Behavior

### Search Results Ordering:
1. NIFTY 50 companies listed first
2. Then NIFTY 500 companies
3. Then alphabetically by name

### Error Handling:
- **400 Bad Request**: Invalid query parameters (empty query, limit > 100)
- **401 Unauthorized**: Missing or invalid JWT token
- **404 Not Found**: Company not found
- **500 Internal Server Error**: Database or server errors

### Performance:
- Search should return results in < 500ms
- Company details should load in < 200ms
- Reports list should load in < 300ms

---

## Database Verification

### Check companies table:
```sql
-- Count total companies
SELECT COUNT(*) FROM companies;
-- Expected: 12

-- List all companies
SELECT name, nse_symbol, is_nifty_50, is_nifty_500
FROM companies
ORDER BY is_nifty_50 DESC, name ASC;

-- Search simulation (case-insensitive)
SELECT name, nse_symbol
FROM companies
WHERE name ILIKE '%bank%'
   OR nse_symbol ILIKE 'bank%'
   OR bse_code ILIKE 'bank%';
```

---

## Troubleshooting

### Issue: No companies found in search
**Solution**: Run seed script: `python -m app.scripts.seed_test_companies`

### Issue: 401 Unauthorized error
**Solution**:
1. Login via `/api/v1/auth/login`
2. Copy access_token
3. Click "Authorize" in Swagger UI
4. Enter: `Bearer <token>`

### Issue: 404 Company not found
**Solution**:
1. Verify company exists: `GET /api/v1/companies/search?q=<name>`
2. Use correct UUID from search results

### Issue: Empty reports list
**Solution**: Upload a report first via `POST /api/v1/reports/upload`

---

## Success Criteria

✅ All 3 endpoints return 200 OK with valid authentication
✅ Search returns correct companies based on query
✅ Company details include accurate information
✅ Reports list shows uploaded reports
✅ Error handling works correctly (401, 404, 500)
✅ Pagination works correctly
✅ NIFTY 500 filter works correctly
✅ Results are ordered correctly (NIFTY 50 > NIFTY 500 > Alphabetical)

---

## API Endpoints Summary

### Phase 5 - Company Search (NEW) ✅
- ✅ `GET /api/v1/companies/search` - Search companies
- ✅ `GET /api/v1/companies/{company_id}` - Get company details
- ✅ `GET /api/v1/companies/{company_id}/reports` - Get company reports

### Total API Endpoints: 15
- Authentication: 3 endpoints
- Companies: 3 endpoints (NEW)
- Reports: 4 endpoints
- Analysis: 5 endpoints

---

## Next Steps

After verifying Phase 5 works correctly:

1. **Phase 6**: Begin Frontend Foundation (Next.js setup)
2. **Phase 13**: Seed full NIFTY 500 data (500 companies)
3. **Phase 14**: Add automated tests (pytest)

---

**Phase 5 Status**: ✅ COMPLETE
**Implementation Date**: February 6, 2026
**Total Lines Added**: ~450 lines
**Files Created**: 4 new files
**Files Modified**: 2 files
