# RedFlag AI - Local Setup Checklist

Use this checklist to verify your local setup is working correctly.

---

## ✅ **Pre-Requisites**

- [ ] Python 3.11 installed (`python --version`)
- [ ] Node.js 20.x installed (`node --version`)
- [ ] PostgreSQL database running (local or Supabase)
- [ ] Redis running (local or Upstash)
- [ ] Google Gemini API key obtained
- [ ] Git repository cloned at `D:\redflags`

---

## ✅ **Backend Setup**

### Environment
- [ ] Virtual environment created (`python -m venv venv`)
- [ ] Virtual environment activated (`venv\Scripts\activate`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created from `.env.example`
- [ ] All environment variables filled in `.env`

### API Keys & Secrets
- [ ] `DATABASE_URL` set (PostgreSQL connection string)
- [ ] `REDIS_URL` / `CELERY_BROKER_URL` set
- [ ] `GEMINI_API_KEY` set
- [ ] `JWT_SECRET_KEY` set (random secret)
- [ ] `BREVO_API_KEY` set (optional for emails)
- [ ] `VAPID_PRIVATE_KEY` and `VAPID_PUBLIC_KEY` generated and set

### Database
- [ ] Setup verification passed (`python scripts/verify_setup.py`)
- [ ] Migration completed (`python scripts/run_migration.py`)
- [ ] All tables created (users, companies, watchlist_items, portfolios, etc.)
- [ ] Companies seeded (`python scripts/seed_companies.py --source manual --sample 25`)
- [ ] Annual reports seeded (`python scripts/seed_annual_reports.py --mode sample`)

### Services Running
- [ ] FastAPI server running (`uvicorn app.main:app --reload`)
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Celery worker running (`celery -A app.celery_app worker --pool=solo --loglevel=info`)
- [ ] Celery beat running (`celery -A app.celery_app beat --loglevel=info`)

---

## ✅ **Frontend Setup**

### Environment
- [ ] Dependencies installed (`npm install`)
- [ ] `.env.local` file created with `NEXT_PUBLIC_API_URL=http://localhost:8000`
- [ ] Development server running (`npm run dev`)
- [ ] Frontend accessible at http://localhost:3000

### Pages Loading
- [ ] Landing page loads (/)
- [ ] Login page loads (/login)
- [ ] Signup page loads (/signup)
- [ ] Dashboard loads (/dashboard)
- [ ] Analyze page loads (/analyze)
- [ ] Watchlist page loads (/watchlist)
- [ ] Portfolio page loads (/portfolio)
- [ ] Fraud cases page loads (/learn)
- [ ] Settings page loads (/settings)

---

## ✅ **API Testing (via http://localhost:8000/docs)**

### Authentication
- [ ] POST /api/v1/auth/signup - Create test account
- [ ] POST /api/v1/auth/login - Login with test account
- [ ] GET /api/v1/auth/me - Get current user (with JWT token)

### Companies
- [ ] GET /api/v1/companies/search?q=reliance - Search for Reliance
- [ ] GET /api/v1/companies/{id} - Get company details
- [ ] GET /api/v1/companies/{id}/reports - List annual reports

### Watchlist
- [ ] GET /api/v1/watchlist - Get empty watchlist
- [ ] POST /api/v1/watchlist - Add company to watchlist
- [ ] GET /api/v1/watchlist/preferences - Get notification preferences
- [ ] PATCH /api/v1/watchlist/preferences - Update preferences

### Portfolio
- [ ] POST /api/v1/portfolio/upload - Upload test CSV file
- [ ] GET /api/v1/portfolio - List portfolios
- [ ] GET /api/v1/portfolio/{id} - Get portfolio details
- [ ] DELETE /api/v1/portfolio/{id} - Delete portfolio

### Fraud Cases
- [ ] GET /api/v1/fraud-cases - List all fraud cases (should return 6)
- [ ] GET /api/v1/fraud-cases/{id} - Get case details
- [ ] POST /api/v1/fraud-cases/pattern-match - Match fraud patterns
- [ ] GET /api/v1/fraud-cases/patterns - Get all patterns

### Users
- [ ] GET /api/v1/users/profile - Get profile
- [ ] PATCH /api/v1/users/profile - Update profile
- [ ] POST /api/v1/users/password - Change password
- [ ] GET /api/v1/users/export-data - Request data export

---

## ✅ **Feature Testing (Frontend)**

### User Authentication
- [ ] Sign up with new email
- [ ] Receive JWT token
- [ ] Login with credentials
- [ ] Logout functionality
- [ ] Protected routes redirect to login

### Company Search
- [ ] Search bar works on analyze page
- [ ] Autocomplete shows results
- [ ] Can click company to view details
- [ ] Popular companies section displays

### Watchlist
- [ ] Can add company to watchlist
- [ ] Watchlist displays added companies
- [ ] Can remove company from watchlist
- [ ] Alert toggle works
- [ ] Alert history displays

### Portfolio
- [ ] CSV upload area displays (Premium feature notice)
- [ ] Can upload test CSV file
- [ ] Portfolio parses correctly
- [ ] Shows matched and unmatched symbols
- [ ] Displays risk scores
- [ ] Can delete portfolio

### Fraud Cases
- [ ] All 6 cases display
- [ ] Can filter by sector
- [ ] Can search by company name
- [ ] Can view case details
- [ ] Pattern matching form works
- [ ] Similarity scores calculate

### Settings
- [ ] Profile section shows user data
- [ ] Can update name and email
- [ ] Can change password
- [ ] Notification preferences display
- [ ] Can toggle email/push notifications
- [ ] Can request data export
- [ ] Can delete account (with confirmation)

---

## ✅ **Background Tasks Testing**

### Celery Worker
- [ ] Worker connected to Redis
- [ ] No error messages in logs
- [ ] Can see registered tasks

### Celery Beat
- [ ] Beat schedule configured
- [ ] Shows scheduled tasks:
  - check-watchlist-alerts-daily (8 AM UTC)
  - send-weekly-digest (Monday 9 AM UTC)

### Manual Task Execution
```bash
cd backend
python -c "from app.tasks.watchlist_tasks import check_watchlist_alerts; print(check_watchlist_alerts())"
```
- [ ] Task executes without errors
- [ ] Alerts created if score changes detected

---

## ✅ **Email Testing (Optional - if Brevo configured)**

- [ ] BREVO_API_KEY set in .env
- [ ] Can send test email
- [ ] Watchlist alert email received
- [ ] Email formatting looks correct
- [ ] Weekly digest email works

---

## ✅ **Push Notifications Testing (Optional - if VAPID configured)**

- [ ] VAPID keys generated and set
- [ ] Service worker registered in browser
- [ ] Can save push subscription
- [ ] Push notification received when alert triggered
- [ ] Notification click navigates to watchlist

---

## ✅ **Database Verification**

Run these SQL queries to verify data:

```sql
-- Check companies
SELECT COUNT(*) FROM companies;
-- Should be 25

-- Check annual reports
SELECT COUNT(*) FROM annual_reports;
-- Should be ~10

-- Check users
SELECT email, subscription_tier FROM users;
-- Should show your test account

-- Check watchlist
SELECT * FROM watchlist_items;
-- Should show companies you added

-- Check portfolios
SELECT * FROM portfolios;
-- Should show uploaded portfolios

-- Check fraud cases data loaded
SELECT COUNT(*) FROM ...
-- Note: Fraud cases are in JSON file, not database
```

- [ ] Companies table has 25 records
- [ ] Annual reports table has ~10 records
- [ ] Users table has test account
- [ ] Watchlist items exist if you added any
- [ ] Portfolios exist if you uploaded any

---

## ✅ **Performance Checks**

- [ ] Backend API responds in <500ms
- [ ] Frontend pages load in <2s
- [ ] File upload works for files up to 10MB
- [ ] No console errors in browser
- [ ] No Python errors in terminal

---

## ✅ **Security Checks**

- [ ] JWT tokens required for protected routes
- [ ] Can't access other user's data
- [ ] Password change requires old password
- [ ] Account deletion requires email confirmation
- [ ] CORS configured correctly

---

## 🚨 **Common Issues**

If any checks fail, refer to these solutions:

### Database Connection Failed
```bash
# Check PostgreSQL is running
# Windows: services.msc → PostgreSQL
# Verify DATABASE_URL in .env
```

### Redis Connection Failed
```bash
# Check Redis is running
# Windows: Download from https://redis.io/download
# Verify REDIS_URL in .env
```

### Celery Worker Not Starting
```bash
# Use --pool=solo on Windows
celery -A app.celery_app worker --pool=solo --loglevel=info
```

### Migration Failed
```bash
# Manually run migration
cd backend
alembic upgrade head
```

### Frontend Build Errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules
npm install
```

---

## ✅ **Ready for Next Steps**

Once all checks pass:

### Option A: Continue Development
- [ ] Add more features
- [ ] Implement remaining items from plan
- [ ] Add Razorpay payment integration

### Option B: Deploy
- [ ] Review deployment documentation
- [ ] Setup production environment
- [ ] Configure cloud services
- [ ] Deploy Docker containers

### Option C: Add Real Data
- [ ] Download NIFTY 500 CSV
- [ ] Seed all 500 companies
- [ ] Scrape real annual reports
- [ ] Pre-compute analysis cache

---

## 📊 **Final Verification**

- [ ] **All Pre-Requisites** checked ✅
- [ ] **Backend Setup** complete ✅
- [ ] **Frontend Setup** complete ✅
- [ ] **API Testing** passed ✅
- [ ] **Feature Testing** passed ✅
- [ ] **Background Tasks** working ✅
- [ ] **Database** verified ✅
- [ ] **Performance** acceptable ✅
- [ ] **Security** configured ✅

---

## 🎉 **Congratulations!**

If all checks pass, your local development environment is fully functional!

**What you can do now:**
1. ✅ Develop new features
2. ✅ Test existing features
3. ✅ Analyze companies (with sample data)
4. ✅ Use watchlist and portfolio features
5. ✅ Browse fraud cases
6. ✅ Configure notifications

**Next recommended steps:**
- Review `PROGRESS_SUMMARY.md` for remaining items
- Follow `SETUP_LOCAL.md` for daily workflow
- Check `IMPLEMENTATION_SUMMARY.md` for technical details

---

**Your RedFlag AI local instance is ready! 🚀**
