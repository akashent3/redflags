# RedFlag AI - Testing Guide

**Last Updated:** 2026-02-16
**For Version:** 1.0.0 (All 10 Features Complete)

---

## 🧪 Pre-Testing Setup

### 1. Run SQL Migrations

```sql
-- Connect to your PostgreSQL database
psql -U your_user -d redflags_db

-- Add admin fields to users table
ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE users ADD COLUMN avatar_url VARCHAR(500);

-- Create fraud_cases table
\i backend/sql/create_fraud_cases_table.sql

-- Create an admin user
UPDATE users SET is_admin = TRUE WHERE email = 'admin@example.com';

-- Verify changes
\d users
SELECT * FROM users WHERE is_admin = TRUE;
```

### 2. Set Environment Variables

Create/update `backend/.env`:
```env
# Existing variables
DATABASE_URL=postgresql://user:password@localhost:5432/redflags_db
SECRET_KEY=your-secret-key
FINEDGE_API_KEY=your-finedge-key
GEMINI_API_KEY=your-gemini-key

# R2 Storage
CLOUDFLARE_ACCOUNT_ID=your-account-id
R2_ACCESS_KEY_ID=your-access-key
R2_SECRET_ACCESS_KEY=your-secret-key
R2_BUCKET_NAME=redflags-storage

# Email Service (NEW)
BREVO_API_KEY=your-brevo-api-key
FROM_EMAIL=noreply@redflag-ai.com
FROM_NAME=RedFlag AI
```

### 3. Restart Backend Server

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload
```

---

## 📋 Feature Testing Checklist

### Feature 1: Admin User Support ✅

**Test 1.1: Admin Login**
```bash
# Login as admin user
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=yourpassword"

# Expected: 200 OK with access_token
# Save the token as ADMIN_TOKEN
```

**Test 1.2: Verify Admin Access**
```bash
# Get admin stats (should work for admin)
curl -X GET http://localhost:8000/api/v1/admin/stats \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Expected: 200 OK with system statistics

# Try as non-admin user (should fail)
curl -X GET http://localhost:8000/api/v1/admin/stats \
  -H "Authorization: Bearer $USER_TOKEN"

# Expected: 403 Forbidden
```

---

### Feature 2: Latest Analysis Endpoint ✅

**Test 2.1: Get Latest Analysis**
```bash
# Replace {company_id} with actual company UUID
curl -X GET "http://localhost:8000/api/v1/companies/{company_id}/latest-analysis" \
  -H "Authorization: Bearer $USER_TOKEN"

# Expected: 200 OK with analysis data
# {
#   "analysis_id": "uuid",
#   "risk_score": 45,
#   "risk_level": "MEDIUM",
#   "created_at": "2025-02-16T10:30:00",
#   "fiscal_year": 2024
# }
```

**Test 2.2: Company Without Analysis**
```bash
# Use company_id that has no analysis
curl -X GET "http://localhost:8000/api/v1/companies/{company_id_no_analysis}/latest-analysis" \
  -H "Authorization: Bearer $USER_TOKEN"

# Expected: 200 OK with null analysis_id
# {
#   "analysis_id": null
# }
```

---

### Feature 3: Portfolio Real-Time Prices ✅

**Test 3.1: Fetch Portfolio with Prices**
```bash
# Get portfolios (should show real-time prices)
curl -X GET http://localhost:8000/api/v1/portfolio/ \
  -H "Authorization: Bearer $USER_TOKEN"

# Expected: 200 OK with holdings containing:
# - current_price
# - current_value
# - pnl
# - pnl_percent
# - price_change
# - price_change_percent
```

**Test 3.2: Upload CSV**
```bash
# Upload broker CSV
curl -X POST http://localhost:8000/api/v1/portfolio/upload \
  -H "Authorization: Bearer $USER_TOKEN" \
  -F "file=@test_portfolio.csv" \
  -F "portfolio_name=Test Portfolio"

# Expected: 200 OK with:
# {
#   "portfolio_id": "uuid",
#   "holdings_parsed": 10,
#   "holdings_matched": 9,
#   "unmatched_symbols": ["UNKNOWN"]
# }
```

**Sample CSV (test_portfolio.csv):**
```csv
Symbol,Quantity,Avg Price
HDFCBANK,50,1500
INFY,100,1400
TCS,80,3200
RELIANCE,30,2400
```

---

### Feature 4: FraudCase Database Model ✅

**Test 4.1: Verify Table Creation**
```sql
-- In PostgreSQL
SELECT * FROM fraud_cases;

-- Expected: Empty table with correct schema
\d fraud_cases

-- Expected columns:
-- id, case_id, company_name, year, sector, fraud_type,
-- stock_decline_percent, market_cap_lost_cr, red_flags_detected,
-- timeline, lessons_learned, pdf_url, created_at
```

---

### Feature 5: Fraud Case Admin Script ✅

**Test 5.1: Run Script**
```bash
cd backend

# Analyze a fraud case PDF
python scripts/analyze_fraud_case.py \
    --symbol SATYAM \
    --pdf ../data/fraud_cases/sample_fraud_report.pdf \
    --year 2009 \
    --fraud-type "Accounting Fraud" \
    --sector "IT Services" \
    --stock-decline -97.4 \
    --market-cap-lost 14000

# Expected: Console output showing:
# - PDF upload to R2
# - FinEdge data fetch
# - Flag calculation
# - Gemini analysis
# - Database save
```

**Test 5.2: Verify Database Entry**
```sql
SELECT case_id, company_name, year, fraud_type,
       json_array_length(red_flags_detected) as flags_count
FROM fraud_cases
ORDER BY created_at DESC
LIMIT 1;

-- Expected: One row with fraud case data
```

---

### Feature 6: Pattern Matching Endpoint ✅

**Test 6.1: List Fraud Cases**
```bash
curl -X GET http://localhost:8000/api/v1/fraud-cases/ \
  -H "Authorization: Bearer $USER_TOKEN"

# Expected: 200 OK with array of fraud cases
```

**Test 6.2: Pattern Match Analysis**
```bash
# Replace {analysis_id} with actual analysis UUID
curl -X POST "http://localhost:8000/api/v1/fraud-cases/pattern-match/{analysis_id}" \
  -H "Authorization: Bearer $USER_TOKEN"

# Expected: 200 OK with similarity results
# {
#   "analysis_id": "uuid",
#   "risk_level": "HIGH",
#   "message": "⚠️ HIGH RISK: 65% similarity...",
#   "total_matches": 3,
#   "matches": [...]
# }
```

---

### Feature 7: Settings API Endpoints ✅

**Test 7.1: Get Profile**
```bash
curl -X GET http://localhost:8000/api/v1/users/profile \
  -H "Authorization: Bearer $USER_TOKEN"

# Expected: 200 OK with user profile data
```

**Test 7.2: Update Profile**
```bash
curl -X PATCH http://localhost:8000/api/v1/users/profile \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Updated Name"}'

# Expected: 200 OK with updated profile
```

**Test 7.3: Change Password**
```bash
curl -X POST http://localhost:8000/api/v1/users/password \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "oldpass123",
    "new_password": "NewPass123"
  }'

# Expected: 200 OK with success message
```

**Test 7.4: Upload Avatar**
```bash
curl -X POST http://localhost:8000/api/v1/users/upload-avatar \
  -H "Authorization: Bearer $USER_TOKEN" \
  -F "file=@test_avatar.jpg"

# Expected: 200 OK with R2 URL
# {
#   "avatar_url": "https://pub-xxx.r2.dev/avatars/user-id.jpg",
#   "message": "Avatar uploaded successfully"
# }
```

**Test 7.5: Request Data Export**
```bash
curl -X GET http://localhost:8000/api/v1/users/export-data \
  -H "Authorization: Bearer $USER_TOKEN"

# Expected: 200 OK with task ID
# {
#   "message": "Data export started...",
#   "task_id": "celery-task-id",
#   "estimated_time": "5-10 minutes"
# }
```

**Test 7.6: Delete Account**
```bash
curl -X DELETE "http://localhost:8000/api/v1/users/account?confirmation=user@example.com" \
  -H "Authorization: Bearer $USER_TOKEN"

# Expected: 204 No Content
# WARNING: This will delete the user account!
```

---

### Feature 8: Brevo Email Service ✅

**Test 8.1: Send Watchlist Alert Email**
```python
# In Python shell or test script
from app.services.email_service import send_watchlist_alert_email

send_watchlist_alert_email(
    to_email="test@example.com",
    user_name="Test User",
    company_name="Reliance Industries",
    symbol="RELIANCE",
    alert_type="Risk Score Increase",
    severity="WARNING",
    message="Risk score increased from 35 to 62",
    current_score=62,
    previous_score=35
)

# Check email inbox for alert
```

**Test 8.2: Send Weekly Digest**
```python
from app.services.email_service import send_weekly_digest_email

alerts = [
    {
        "company_name": "Reliance",
        "message": "Risk score increased to 62",
        "severity": "WARNING"
    },
    {
        "company_name": "HDFC Bank",
        "message": "New red flag detected",
        "severity": "CRITICAL"
    }
]

send_weekly_digest_email(
    to_email="test@example.com",
    user_name="Test User",
    alerts=alerts
)

# Check email inbox for digest
```

---

### Feature 9: Admin Panel Backend ✅

**Test 9.1: Get System Stats**
```bash
curl -X GET http://localhost:8000/api/v1/admin/stats \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Expected: 200 OK with comprehensive stats
```

**Test 9.2: List Users**
```bash
curl -X GET "http://localhost:8000/api/v1/admin/users?skip=0&limit=50" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Expected: 200 OK with user list
```

**Test 9.3: Update User Subscription**
```bash
curl -X PATCH "http://localhost:8000/api/v1/admin/users/{user_id}/subscription?subscription_tier=premium" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Expected: 200 OK with updated subscription
```

**Test 9.4: Delete User**
```bash
curl -X DELETE "http://localhost:8000/api/v1/admin/users/{user_id}" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Expected: 204 No Content
# WARNING: This deletes the user!
```

**Test 9.5: List Analyses**
```bash
curl -X GET "http://localhost:8000/api/v1/admin/analyses?skip=0&limit=50" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Expected: 200 OK with analysis list
```

**Test 9.6: Delete Fraud Case**
```bash
curl -X DELETE "http://localhost:8000/api/v1/admin/fraud-cases/{case_id}" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Expected: 204 No Content
```

---

### Feature 10: Portfolio Frontend Integration ✅

**Test 10.1: Open Portfolio Page**
1. Navigate to `http://localhost:3000/portfolio`
2. Should see loading spinner initially
3. Should fetch existing portfolios automatically
4. Should display first portfolio with real-time prices

**Test 10.2: Upload CSV**
1. Click "Choose CSV File" button
2. Select a valid broker CSV file
3. Should show "Uploading & Analyzing..." with spinner
4. Should display uploaded portfolio with real-time data
5. If unmatched symbols, should show warning message

**Test 10.3: Verify Real-Time Prices**
1. Check that "Current Price" column shows live prices
2. Check that P&L is calculated and color-coded:
   - Green for positive P&L
   - Red for negative P&L
3. Check that price change percentage is displayed
4. Verify "Total P&L" summary card shows correct calculation

**Test 10.4: Switch Between Portfolios**
1. If multiple portfolios exist, dropdown should be visible
2. Select different portfolio from dropdown
3. Holdings table should update immediately
4. Summary cards should recalculate

**Test 10.5: Upload New Portfolio**
1. Click "Upload New Portfolio" button
2. Should reset to upload screen
3. Upload new CSV
4. Should add to portfolio list

**Test 10.6: Error Handling**
1. Upload invalid CSV format
2. Should display error message in red box
3. Upload CSV with invalid symbols
4. Should display warning about unmatched symbols

---

## 🐛 Common Issues & Solutions

### Issue 1: "403 Forbidden" on Admin Endpoints
**Solution:** Verify user has `is_admin = TRUE` in database:
```sql
UPDATE users SET is_admin = TRUE WHERE email = 'admin@example.com';
```

### Issue 2: Real-Time Prices Show "N/A"
**Solution:** Check FinEdge API credentials and symbol mapping file:
```bash
# Verify symbol mapping exists
cat backend/data/symbol_mapping.json

# Test FinEdge API directly
curl https://api.finedge.in/api/v1/stocks \
  -H "X-API-Key: $FINEDGE_API_KEY"
```

### Issue 3: Avatar Upload Fails
**Solution:** Verify R2 credentials and bucket permissions:
```env
CLOUDFLARE_ACCOUNT_ID=your-account-id
R2_ACCESS_KEY_ID=your-access-key
R2_SECRET_ACCESS_KEY=your-secret-key
R2_BUCKET_NAME=redflags-storage
```

### Issue 4: Email Sending Fails
**Solution:** Check Brevo API key and credentials:
```bash
# Test Brevo API
curl https://api.brevo.com/v3/account \
  -H "api-key: $BREVO_API_KEY"
```

### Issue 5: Pattern Matching Returns No Matches
**Solution:** Ensure fraud_cases table has data:
```sql
SELECT COUNT(*) FROM fraud_cases;

# If empty, run fraud case analysis script
python scripts/analyze_fraud_case.py --symbol SATYAM ...
```

### Issue 6: Portfolio Frontend Not Fetching
**Solution:** Check CORS settings and API URL:
```env
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## 📊 Performance Testing

### Load Test Portfolio Endpoint
```bash
# Install Apache Bench
apt-get install apache2-utils

# Test portfolio endpoint
ab -n 100 -c 10 \
  -H "Authorization: Bearer $USER_TOKEN" \
  http://localhost:8000/api/v1/portfolio/

# Expected: < 500ms average response time
```

### Test Real-Time Price Fetching
```bash
# Time the portfolio fetch with 10 holdings
time curl -X GET http://localhost:8000/api/v1/portfolio/ \
  -H "Authorization: Bearer $USER_TOKEN"

# Expected: < 3 seconds for 10 holdings
```

---

## ✅ Final Checklist

Before marking implementation as complete:

- [ ] All SQL migrations applied successfully
- [ ] Admin user created and verified
- [ ] All 10 features tested and working
- [ ] Real-time prices fetching correctly
- [ ] Pattern matching algorithm functional
- [ ] Email service configured and tested
- [ ] Avatar uploads working to R2
- [ ] Portfolio frontend displaying real-time data
- [ ] Admin endpoints protected and functional
- [ ] No regression in existing features
- [ ] Error messages displaying correctly
- [ ] Loading states working properly
- [ ] Documentation complete and accurate

---

**Testing Complete! 🎉**

All 10 features have been implemented and are ready for production deployment.

For deployment checklist, see `DEPLOYMENT_GUIDE.md`.
For API documentation, see `API_DOCUMENTATION.md`.
