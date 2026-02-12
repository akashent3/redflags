# RedFlag AI - Complete Setup & Run Guide

## Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL (running)
- Redis (running)
- FinEdge API Token
- Gemini API Key

---

## 1. Environment Setup

### Backend Environment Variables

Create/update `.env` in `/backend` directory:

```bash
# Database
DATABASE_URL=postgresql+pg8000://user:password@localhost:5432/redflags

# Redis & Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# AI APIs
GEMINI_API_KEY=your_gemini_api_key_here
FINEDGE_API_TOKEN=your_finedge_token_here

# Storage (Cloudflare R2)
R2_ACCESS_KEY_ID=your_r2_access_key
R2_SECRET_ACCESS_KEY=your_r2_secret_key
R2_BUCKET_NAME=your_bucket_name
R2_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
R2_PUBLIC_URL=https://your-public-url.r2.dev

# JWT
JWT_SECRET_KEY=your-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

### Frontend Environment Variables

Create/update `.env.local` in `/frontend` directory:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## 2. Installation

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install
```

---

## 3. Starting Services

### Option A: Manual Start (Recommended for Testing)

Open 4 terminal windows:

**Terminal 1: Backend API**
```bash
cd /home/user/redflags/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2: Celery Worker**
```bash
cd /home/user/redflags/backend
source venv/bin/activate
celery -A app.celery_app worker --loglevel=info
```

**Terminal 3: Redis (if not running)**
```bash
redis-server
```

**Terminal 4: Frontend**
```bash
cd /home/user/redflags/frontend
npm run dev
```

### Option B: Using Screen/Tmux

```bash
# Start backend
screen -dmS backend bash -c "cd /home/user/redflags/backend && source venv/bin/activate && uvicorn app.main:app --reload"

# Start Celery
screen -dmS celery bash -c "cd /home/user/redflags/backend && source venv/bin/activate && celery -A app.celery_app worker --loglevel=info"

# Start frontend
screen -dmS frontend bash -c "cd /home/user/redflags/frontend && npm run dev"

# View logs
screen -r backend   # Ctrl+A, D to detach
screen -r celery
screen -r frontend
```

---

## 4. Verify Services

### Check Backend
```bash
curl http://localhost:8000/docs
# Should show FastAPI Swagger UI
```

### Check Frontend
```bash
curl http://localhost:3000
# Should return HTML
```

### Check Celery
Look for this in Celery terminal:
```
[tasks]
  . app.tasks.analysis_tasks.analyze_report_task
  . app.tasks.analysis_tasks.analyze_company_by_symbol_task
```

---

## 5. Testing the Flow

### Test 1: User Registration & Login

```bash
# Register a new user
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!@#",
    "full_name": "Test User"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=Test123!@#"

# Save the access_token from response
```

### Test 2: Company Search (API)

```bash
# Search for companies
curl -X GET "http://localhost:8000/api/v1/companies/finedge/search?q=reliance&limit=5" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Test 3: Analyze by Symbol (API)

```bash
# Trigger analysis for a company
curl -X POST http://localhost:8000/api/v1/analysis/analyze-symbol/RELIANCE \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Response will include task_id
# {"task_id": "abc-123-def", "status": "PENDING", ...}

# Check task status
curl -X GET http://localhost:8000/api/v1/analysis/task/abc-123-def \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Test 4: Complete UI Flow

1. **Open Browser**
   ```
   http://localhost:3000
   ```

2. **Register/Login**
   - Click "Sign Up"
   - Create account
   - Login

3. **Analyze a Company**
   - Go to "Analyze" page
   - Click "Search Company" tab
   - Search for "TCS" or "Reliance"
   - Click "Analyze" button
   - Wait 1-2 minutes (watch Celery logs)
   - Should redirect to report page

4. **Verify Results**
   - Check risk score (0-100)
   - View spider chart (8 categories)
   - See red flags list
   - Check category breakdown

---

## 6. Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'app.services.gemini_analyzer'"

**Solution:** Copy the gemini_analyzer from mini_app:
```bash
cp /home/user/redflags/mini_app/gemini_analyzer.py /home/user/redflags/backend/app/services/
```

### Issue: FinEdge API returns 401/403

**Solution:** Check your `FINEDGE_API_TOKEN` in `.env` file

### Issue: NSE fetch fails

**Symptoms:** Analysis fails with "No annual report found"

**Solution:** 
- NSE India website may be blocking requests
- Check `backend/app/services/nse_client.py` headers
- Try different company symbols
- Fallback: Use PDF upload instead

### Issue: Celery not picking up tasks

**Solution:**
```bash
# Restart Celery worker
# Kill existing worker
pkill -f celery

# Start fresh
cd backend
celery -A app.celery_app worker --loglevel=info
```

### Issue: Database connection errors

**Solution:**
```bash
# Check PostgreSQL is running
pg_isready

# Check connection string in .env
# Verify database exists
psql -U user -d redflags -c "SELECT 1;"

# Re-run migrations
cd backend
alembic upgrade head
```

### Issue: Frontend API calls fail (CORS)

**Solution:** Backend already configured for CORS. Check:
- Backend is running on port 8000
- Frontend URL is correct in backend `.env`: `FRONTEND_URL=http://localhost:3000`

---

## 7. Pre-seed NIFTY 500 Companies (Optional)

```bash
cd /home/user/redflags/backend

# Test with 5 companies first
python scripts/seed_nifty500.py --limit 5 --direct --delay 10

# If successful, run for more
python scripts/seed_nifty500.py --limit 50 --delay 10

# Or queue all via Celery (faster, run in background)
python scripts/seed_nifty500.py --limit 100
```

**Monitor Progress:**
```bash
# Watch Celery logs
tail -f celery.log

# Or if running in screen
screen -r celery
```

---

## 8. Production Deployment Checklist

- [ ] Set strong `JWT_SECRET_KEY`
- [ ] Use production database (not SQLite)
- [ ] Set `DEBUG=False`
- [ ] Configure proper CORS origins
- [ ] Use production Redis server
- [ ] Set up Celery with supervisor/systemd
- [ ] Configure Nginx/Apache reverse proxy
- [ ] Set up SSL certificates
- [ ] Configure R2 bucket with proper permissions
- [ ] Monitor Gemini API usage & costs
- [ ] Set up logging and monitoring
- [ ] Create database backups

---

## 9. Quick Start Script

Save this as `start_all.sh`:

```bash
#!/bin/bash

echo "Starting RedFlag AI..."

# Start Redis (if not running)
redis-cli ping > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Starting Redis..."
    redis-server --daemonize yes
fi

# Start Backend
echo "Starting Backend..."
cd /home/user/redflags/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

# Start Celery
echo "Starting Celery..."
celery -A app.celery_app worker --loglevel=info > /tmp/celery.log 2>&1 &
CELERY_PID=$!

# Start Frontend
echo "Starting Frontend..."
cd /home/user/redflags/frontend
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!

echo ""
echo "✅ All services started!"
echo ""
echo "Backend:  http://localhost:8000/docs"
echo "Frontend: http://localhost:3000"
echo ""
echo "Logs:"
echo "  Backend:  tail -f /tmp/backend.log"
echo "  Celery:   tail -f /tmp/celery.log"
echo "  Frontend: tail -f /tmp/frontend.log"
echo ""
echo "PIDs: Backend=$BACKEND_PID Celery=$CELERY_PID Frontend=$FRONTEND_PID"
echo ""
echo "To stop all services:"
echo "  kill $BACKEND_PID $CELERY_PID $FRONTEND_PID"
```

Make it executable:
```bash
chmod +x start_all.sh
./start_all.sh
```

---

## 10. Monitoring & Logs

### View Real-time Logs

```bash
# Backend
tail -f /tmp/backend.log

# Celery (see task progress)
tail -f /tmp/celery.log

# Frontend
tail -f /tmp/frontend.log
```

### Check Service Status

```bash
# Check if services are running
ps aux | grep "uvicorn\|celery\|next"

# Check ports
netstat -tulpn | grep "8000\|3000\|6379"
```

---

## Need Help?

- Check logs for error messages
- Verify all environment variables are set
- Ensure all services (PostgreSQL, Redis) are running
- Test API endpoints individually with curl
- Check Celery worker is picking up tasks

