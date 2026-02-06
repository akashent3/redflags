# Local Development Setup Guide

## 🚀 Complete Step-by-Step Setup

This guide will help you get RedFlag AI running locally on your machine.

---

## Prerequisites

Before starting, ensure you have:

- ✅ Python 3.11 installed
- ✅ Node.js 20.x LTS installed
- ✅ PostgreSQL database running (or Supabase account)
- ✅ Redis running (or Upstash account)
- ✅ Google Gemini API key

---

## Step 1: Clone and Setup Project Structure

```bash
cd D:\redflags

# Verify project structure
dir backend
dir frontend
```

---

## Step 2: Backend Setup

### 2.1 Create Python Virtual Environment

```bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### 2.2 Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected packages:**
- fastapi, uvicorn
- sqlalchemy, alembic, psycopg2-binary
- celery, redis
- pandas, openpyxl
- sib-api-v3-sdk (Brevo)
- pywebpush, py-vapid
- google-generativeai
- PyMuPDF, Pillow
- boto3

### 2.3 Setup Environment Variables

Copy `.env.example` to `.env`:

```bash
copy .env.example .env
```

Edit `.env` and fill in your credentials:

```bash
# Database (Supabase or local PostgreSQL)
DATABASE_URL=postgresql://postgres:password@localhost:5432/redflags

# Redis (Upstash or local)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# JWT Secret
JWT_SECRET_KEY=your-secret-key-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Cloudflare R2 (optional for now)
R2_ACCESS_KEY_ID=your_r2_key
R2_SECRET_ACCESS_KEY=your_r2_secret
R2_BUCKET_NAME=redflags-pdfs
R2_ENDPOINT_URL=https://...
R2_PUBLIC_URL=https://...

# Brevo Email (get from https://app.brevo.com/)
BREVO_API_KEY=xkeysib-your-key-here
FROM_EMAIL=noreply@redflag-ai.com
FROM_NAME=RedFlag AI

# Web Push Notifications
VAPID_PRIVATE_KEY=your_vapid_private_key
VAPID_PUBLIC_KEY=your_vapid_public_key
VAPID_CLAIM_EMAIL=support@redflag-ai.com
```

### 2.4 Generate VAPID Keys

```bash
pip install py-vapid
vapid --gen

# Copy the output keys to your .env file
# Private Key: ...
# Public Key: ...
```

---

## Step 3: Database Setup

### 3.1 Verify Setup

```bash
cd backend
python scripts/verify_setup.py
```

This checks:
- ✅ Environment variables set
- ✅ Dependencies installed
- ✅ Database connection works
- ✅ Redis connection works

### 3.2 Run Database Migration

```bash
python scripts/run_migration.py
```

This will:
- Create all database tables
- Verify tables created successfully
- Show table schema

**Expected output:**
```
✅ Migration completed successfully!
✅ All tables verified successfully!

Database is ready with all tables:
   • Core tables (users, companies, reports, analysis)
   • Watchlist tables (items, alerts, preferences)
   • Portfolio tables (portfolios, holdings)
```

### 3.3 Seed Companies

Start with 25 sample companies:

```bash
python scripts/seed_companies.py --source manual --sample 25
```

Or seed from CSV (if you have NIFTY 500 data):

```bash
python scripts/seed_companies.py --source csv --file data/nifty500.csv
```

**Expected output:**
```
✅ RELIANCE       Reliance Industries                       (added)
✅ TCS            Tata Consultancy Services                 (added)
✅ HDFCBANK       HDFC Bank                                 (added)
...
📊 SEEDING SUMMARY
✅ Added:   25
```

### 3.4 Seed Sample Annual Reports

```bash
python scripts/seed_annual_reports.py --mode sample
```

**Expected output:**
```
✅ RELIANCE FY2023: Added
✅ TCS FY2023: Added
...
📊 Database Statistics
📈 Companies: 25
📄 Annual Reports: 10
```

---

## Step 4: Start Backend Services

Open **4 separate terminals** (all with venv activated):

### Terminal 1: FastAPI Server

```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify:** Open http://localhost:8000/docs

### Terminal 2: Celery Worker

```bash
cd backend
venv\Scripts\activate
celery -A app.celery_app worker --loglevel=info --pool=solo
```

**Note:** Use `--pool=solo` on Windows

### Terminal 3: Celery Beat (Scheduled Tasks)

```bash
cd backend
venv\Scripts\activate
celery -A app.celery_app beat --loglevel=info
```

### Terminal 4: (Optional) Celery Flower (Monitoring)

```bash
cd backend
venv\Scripts\activate
pip install flower
celery -A app.celery_app flower --port=5555
```

**Verify:** Open http://localhost:5555

---

## Step 5: Frontend Setup

### 5.1 Install Dependencies

```bash
cd frontend
npm install
```

### 5.2 Setup Environment Variables

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### 5.3 Start Development Server

```bash
npm run dev
```

**Verify:** Open http://localhost:3000

---

## Step 6: Verify Everything Works

### 6.1 Test Backend APIs

Open http://localhost:8000/docs and test:

1. **GET /api/v1/companies/search?q=reliance**
   - Should return Reliance Industries

2. **POST /api/v1/auth/signup**
   ```json
   {
     "email": "test@example.com",
     "password": "testpassword123",
     "full_name": "Test User"
   }
   ```
   - Should create a new user

3. **POST /api/v1/auth/login**
   ```json
   {
     "email": "test@example.com",
     "password": "testpassword123"
   }
   ```
   - Should return JWT token

4. **GET /api/v1/fraud-cases**
   - Should return 6 fraud cases

5. **GET /api/v1/watchlist** (with Authorization header)
   - Should return empty watchlist

### 6.2 Test Frontend

1. **Landing Page** (http://localhost:3000)
   - Should show hero section, features, pricing

2. **Sign Up** (http://localhost:3000/signup)
   - Create account, should redirect to dashboard

3. **Dashboard** (http://localhost:3000/dashboard)
   - Should show welcome message

4. **Analyze Page** (http://localhost:3000/analyze)
   - Should show company search and file upload

5. **Watchlist** (http://localhost:3000/watchlist)
   - Should show empty watchlist

6. **Portfolio** (http://localhost:3000/portfolio)
   - Should show CSV upload (Premium feature)

7. **Fraud Cases** (http://localhost:3000/learn)
   - Should show 6 fraud cases

8. **Settings** (http://localhost:3000/settings)
   - Should show profile, subscription, notifications

---

## Step 7: Test Key Features

### 7.1 Test Portfolio Upload

1. Create test CSV file `test_portfolio.csv`:
   ```csv
   Symbol,Quantity,Avg Price
   RELIANCE,10,2500
   TCS,5,3500
   INFY,20,1500
   ```

2. Upload via API:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/portfolio/upload" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -F "file=@test_portfolio.csv" \
     -F "portfolio_name=Test Portfolio"
   ```

3. Verify response shows matched/unmatched companies

### 7.2 Test Watchlist Alerts

1. Add company to watchlist:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/watchlist" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"company_id": "COMPANY_UUID", "alert_enabled": true}'
   ```

2. Manually trigger alert check:
   ```bash
   cd backend
   python -c "from app.tasks.watchlist_tasks import check_watchlist_alerts; check_watchlist_alerts()"
   ```

### 7.3 Test Email Sending

1. Configure Brevo API key in `.env`

2. Test email:
   ```python
   from app.services.email_service import send_email
   send_email(
       to_email="your-email@example.com",
       to_name="Test User",
       subject="Test Email",
       html_content="<h1>It works!</h1>"
   )
   ```

---

## Common Issues & Solutions

### Issue: `alembic: command not found`

**Solution:**
```bash
pip install alembic
# OR
python -m alembic upgrade head
```

### Issue: Database connection refused

**Solution:**
1. Check PostgreSQL is running
2. Verify DATABASE_URL in .env
3. Test connection: `psql -U postgres -d redflags`

### Issue: Redis connection refused

**Solution:**
1. **Ubuntu/Debian:** `sudo systemctl start redis`
2. **macOS:** `brew services start redis`
3. **Windows:** Download from https://redis.io/download

### Issue: Celery worker fails on Windows

**Solution:**
Use `--pool=solo` flag:
```bash
celery -A app.celery_app worker --loglevel=info --pool=solo
```

### Issue: Port 8000 already in use

**Solution:**
```bash
uvicorn app.main:app --reload --port 8001
```

### Issue: CORS errors in frontend

**Solution:**
1. Verify FRONTEND_URL in backend .env
2. Check CORS middleware in `app/main.py`
3. Ensure frontend uses correct API URL in `.env.local`

### Issue: CSV upload fails

**Solution:**
1. Verify pandas installed: `pip install pandas openpyxl`
2. Check CSV format (Symbol, Quantity, Avg Price columns)
3. Ensure Premium subscription tier for user

---

## Development Workflow

### Daily Development Routine

1. **Start Services:**
   ```bash
   # Terminal 1: Backend
   cd backend && venv\Scripts\activate && uvicorn app.main:app --reload

   # Terminal 2: Celery
   cd backend && venv\Scripts\activate && celery -A app.celery_app worker --pool=solo

   # Terminal 3: Frontend
   cd frontend && npm run dev
   ```

2. **Make Changes:**
   - Edit backend code → FastAPI auto-reloads
   - Edit frontend code → Next.js hot-reloads
   - Edit database models → Run `alembic revision` and `alembic upgrade head`

3. **Test Changes:**
   - Backend: Use http://localhost:8000/docs
   - Frontend: Use http://localhost:3000
   - Check logs in terminals

4. **Commit Changes:**
   ```bash
   git add .
   git commit -m "Your commit message"
   ```

---

## Next Steps

After local setup is complete:

1. ✅ **Add More Companies:**
   - Download NIFTY 500 CSV from NSE website
   - Seed with: `python scripts/seed_companies.py --source csv --file nifty500.csv`

2. ✅ **Test Analysis Pipeline:**
   - Upload real annual report PDF
   - Wait for Celery to process
   - View results in frontend

3. ✅ **Configure Payment Gateway:**
   - Get Razorpay API keys
   - Add to .env
   - Test payment flow

4. ✅ **Deploy to Production:**
   - See DEPLOYMENT.md for deployment guide
   - Use Docker or cloud platform

---

## Useful Commands

### Backend

```bash
# Check migration status
alembic current

# Create new migration
alembic revision --autogenerate -m "description"

# Upgrade database
alembic upgrade head

# Downgrade by 1 revision
alembic downgrade -1

# Run tests
pytest

# Check code style
black . --check
flake8
```

### Frontend

```bash
# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linter
npm run lint

# Format code
npm run format
```

### Database

```bash
# Connect to database
psql -U postgres -d redflags

# List tables
\dt

# Describe table
\d companies

# Count records
SELECT COUNT(*) FROM companies;
SELECT COUNT(*) FROM annual_reports;
```

---

## Success Checklist

- [ ] All 4 backend services running
- [ ] Frontend accessible at http://localhost:3000
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Database has companies and reports
- [ ] Can sign up and login
- [ ] Can search companies
- [ ] Can upload portfolio CSV
- [ ] Can add to watchlist
- [ ] Can view fraud cases
- [ ] Email notifications work (if Brevo configured)
- [ ] Push notifications work (if VAPID keys set)

---

## Support

If you encounter issues:

1. **Check logs** in terminal windows
2. **Verify environment variables** are set correctly
3. **Ensure all services are running** (PostgreSQL, Redis, FastAPI, Celery)
4. **Review error messages** carefully
5. **Check database tables exist** with migration script

---

**You're all set! Start building! 🚀**
