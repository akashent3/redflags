# Quick Start Guide - Backend Setup

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Setup Environment Variables

Create or update `backend/.env`:

```bash
# Brevo Email (Get API key from https://app.brevo.com/)
BREVO_API_KEY=your_brevo_api_key_here
FROM_EMAIL=noreply@redflag-ai.com
FROM_NAME=RedFlag AI

# Generate VAPID keys (see below)
VAPID_PRIVATE_KEY=your_vapid_private_key
VAPID_PUBLIC_KEY=your_vapid_public_key
VAPID_CLAIM_EMAIL=support@redflag-ai.com
```

**Generate VAPID Keys:**
```bash
pip install py-vapid
vapid --gen
```

Copy the output keys to your `.env` file.

### Step 3: Run Database Migration

```bash
cd backend

# Check current migration status
alembic current

# Run the migration
alembic upgrade head

# Verify tables created
alembic history
```

### Step 4: Start Services

**Terminal 1 - FastAPI Server:**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Celery Worker:**
```bash
cd backend
celery -A app.celery_app worker --loglevel=info
```

**Terminal 3 - Celery Beat (Scheduled Tasks):**
```bash
cd backend
celery -A app.celery_app beat --loglevel=info
```

### Step 5: Verify Everything Works

Open: http://localhost:8000/docs

Test these endpoints:
- ✅ GET `/api/v1/watchlist` - Should return empty watchlist
- ✅ GET `/api/v1/portfolio` - Should return empty portfolios
- ✅ GET `/api/v1/fraud-cases` - Should return 6 fraud cases
- ✅ GET `/api/v1/users/profile` - Should return user profile

---

## 🧪 Quick Test

### Test Portfolio Upload

1. Create a test CSV file `test_portfolio.csv`:
```csv
Symbol,Quantity,Avg Price
RELIANCE,10,2500
TCS,5,3500
INFY,20,1500
```

2. Upload via API:
```bash
curl -X POST "http://localhost:8000/api/v1/portfolio/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test_portfolio.csv" \
  -F "portfolio_name=Test Portfolio"
```

### Test Watchlist Alert

1. Add company to watchlist:
```bash
curl -X POST "http://localhost:8000/api/v1/watchlist" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"company_id": "COMPANY_UUID", "alert_enabled": true}'
```

2. Manually trigger alert check:
```bash
cd backend
python -c "from app.tasks.watchlist_tasks import check_watchlist_alerts; check_watchlist_alerts()"
```

### Test Fraud Pattern Matching

```bash
curl -X POST "http://localhost:8000/api/v1/fraud-cases/pattern-match" \
  -H "Content-Type: application/json" \
  -d '{"company_id": "COMPANY_UUID"}'
```

---

## 🔧 Troubleshooting

### Migration Fails

**Error:** `alembic: command not found`

**Solution:**
```bash
pip install alembic
# OR
python -m alembic upgrade head
```

### Celery Worker Fails

**Error:** `ConnectionRefusedError: [Errno 111] Connection refused`

**Solution:** Start Redis first:
```bash
# Ubuntu/Debian
sudo systemctl start redis

# macOS
brew services start redis

# Windows
# Download and install Redis from https://redis.io/download
```

### Email Not Sending

**Error:** `ApiException: (401) Unauthorized`

**Solution:**
1. Verify BREVO_API_KEY is correct in `.env`
2. Check API key is active in Brevo dashboard
3. Verify FROM_EMAIL is verified in Brevo

### Push Notifications Not Working

**Error:** `vapid_private_key must be set`

**Solution:**
1. Generate VAPID keys: `vapid --gen`
2. Add keys to `.env` file
3. Restart FastAPI server

---

## 📊 Database Schema Check

Verify tables were created:

```bash
# Using psql
psql -U postgres -d redflags -c "\dt"

# Should show:
# - watchlist_items
# - watchlist_alerts
# - notification_preferences
# - portfolios
# - holdings
```

---

## 🎯 What's Next?

After setup is complete:

1. **Test Frontend Integration:**
   - Portfolio upload page
   - Watchlist page
   - Fraud cases page
   - Settings page

2. **Configure Brevo Email Templates:**
   - Test alert emails
   - Test weekly digest
   - Customize HTML templates if needed

3. **Test Push Notifications:**
   - Register service worker in frontend
   - Save push subscription
   - Trigger test alert

4. **Monitor Celery Tasks:**
   - Check logs for errors
   - Verify scheduled tasks run correctly
   - Monitor email delivery rates

---

## 📞 Need Help?

- **API Documentation:** http://localhost:8000/docs
- **Logs:** Check `backend/logs/` directory
- **Database:** Use pgAdmin or psql to inspect tables
- **Celery:** Use Flower for monitoring: `pip install flower && celery -A app.celery_app flower`

---

**Ready to go! 🚀**
