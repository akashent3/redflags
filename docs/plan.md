RedFlag AI - Complete Implementation Plan
Project Overview
RedFlag AI is a forensic accounting scanner that analyzes corporate annual reports using AI to detect financial red flags. This is a full-stack application with 12 pages, 8 core features, and 54 red flag detection checks targeting retail investors.
NOT a dating app - This is an enterprise-grade financial analysis tool for detecting accounting fraud and corporate governance issues.
Technology Stack
Frontend

Framework: Next.js 14 (App Router) + TypeScript
Styling: Tailwind CSS + shadcn/ui components
Charts: Recharts (for gauges/bar charts) + D3.js (for network graphs)
State: React Context + SWR for data fetching
Deployment: Docker containers (local), then Vercel/cloud

Backend

Framework: Python FastAPI
Background Jobs: Celery + Redis
Database: PostgreSQL (via Supabase)
Cache: Redis (via Upstash)
Storage: Cloudflare R2 (for PDFs)
Deployment: Docker containers (local), then Railway/cloud

AI & Processing

LLM: Google Gemini API (user has keys)
PDF Processing: PyMuPDF (native text) + Surya OCR (scanned docs)
OCR Fallback: Google Vision API (optional)

Infrastructure

Local Development: Docker Compose (frontend, backend, postgres, redis)
Production: Docker containers on any cloud provider
Cost: ~$50-100/month initially (vs $300+ with Vercel+Railway)

Project Structure
D:\redflags\
├── frontend/               # Next.js 14 application
│   ├── app/               # App router pages
│   ├── components/        # React components
│   ├── lib/              # Utilities, API client, hooks
│   └── public/           # Static assets
├── backend/              # Python FastAPI
│   ├── app/
│   │   ├── api/         # REST endpoints
│   │   ├── models/      # SQLAlchemy database models
│   │   ├── pdf_pipeline/ # PDF extraction & analysis
│   │   ├── red_flags/   # 54 red flag detectors
│   │   ├── llm/         # Gemini integration
│   │   └── tasks/       # Celery background jobs
│   └── alembic/         # Database migrations
├── docker/              # Docker configuration
├── scripts/             # Setup & seed scripts
└── docs/               # Documentation
Implementation Phases
Phase 0: Environment Setup (2 days)
Goal: Install all required software and get API keys
Steps:

Install Node.js 20.x LTS
Install Python 3.11
Install Docker Desktop
Install VS Code with extensions (ESLint, Prettier, Python, Docker, Tailwind CSS)
Get API keys:

Google Gemini API (user has this)
Supabase (PostgreSQL database)
Upstash (Redis cache)
Cloudflare R2 (PDF storage)



Verification: Run node --version, python --version, docker --version

Phase 1: Backend Foundation (Week 1)
Milestone 1.1: FastAPI Setup (Days 1-2)
Files to create:

backend/requirements.txt - Python dependencies
backend/app/main.py - FastAPI application entry point
backend/app/config.py - Environment configuration
backend/.env - Environment variables (API keys, database URLs)

Key dependencies:

FastAPI, Uvicorn (web framework)
SQLAlchemy, Alembic (database ORM)
Celery, Redis (background jobs)
PyMuPDF, Pillow (PDF processing)
google-generativeai (Gemini API)

Test: Run python -m app.main and access http://localhost:8000/docs
Milestone 1.2: Database Setup (Days 2-3)
Files to create:

backend/app/database.py - Database connection
backend/app/models/user.py - User model
backend/app/models/company.py - Company model
backend/app/models/annual_report.py - Annual report model
backend/app/models/analysis_result.py - Analysis results
backend/app/models/red_flag.py - Red flag records
backend/alembic/env.py - Migration configuration

Database schema (10 tables):

users - Authentication, subscription tier, usage limits
companies - BSE/NSE listed companies, NIFTY 500 data
annual_reports - PDF metadata, fiscal year, storage URL
analysis_results - Risk score, category scores, summary
red_flags - 54 flags with triggered status, evidence, severity
watchlist - User's tracked companies
alerts - Notifications for watchlist changes
related_party_transactions - RPT data for spiderweb graph
subscriptions - Razorpay integration, billing
job_queue - Celery job tracking

Test: Run alembic upgrade head to create all tables
Milestone 1.3: Authentication API (Days 3-4)
Files to create:

backend/app/api/v1/auth.py - Auth endpoints
backend/app/schemas/user.py - Pydantic schemas
backend/app/services/auth_service.py - JWT token logic

Endpoints:

POST /api/v1/auth/signup - Create account
POST /api/v1/auth/login - Login with email/password
POST /api/v1/auth/refresh - Refresh JWT token
GET /api/v1/auth/me - Get current user

Test: Use Postman/Insomnia to signup and login, verify JWT token

Phase 2: PDF Processing Pipeline (Week 2)
Milestone 2.1: PDF Text Extraction (Days 5-6)
Files to create:

backend/app/pdf_pipeline/extractor.py - Main extraction logic
backend/app/pdf_pipeline/ocr_fallback.py - Surya OCR integration
backend/app/storage/r2_client.py - Cloudflare R2 upload

Core logic:

Upload PDF to R2 storage
Try PyMuPDF text extraction (works for 60% of PDFs)
If text is garbled/empty, use Surya OCR
If Surya fails, fallback to Google Vision API
Return structured text with page numbers

Test: Extract text from sample annual report PDF
Milestone 2.2: Section Detection with Gemini (Days 6-7)
Files to create:

backend/app/pdf_pipeline/section_detector.py - LLM-based section detection
backend/app/llm/gemini_client.py - Gemini API wrapper
backend/app/llm/prompts.py - Prompt templates

Detection logic:

Send first 50 pages to Gemini with prompt: "Identify page ranges for: Auditor Report, Cash Flow Statement, Balance Sheet, P&L, Notes to Accounts, Director's Report, Corporate Governance"
Gemini returns JSON: {"auditor_report": [12, 15], "cash_flow": [45, 47], ...}
Refine boundaries by re-checking with Gemini

Test: Detect sections in sample PDF, verify page ranges
Milestone 2.3: Financial Data Extraction (Day 7)
Files to create:

backend/app/pdf_pipeline/data_extractor.py - Extract numbers from tables

Extraction targets:

Revenue, PAT, EBIT from P&L
Cash Flow from Operations (CFO)
Debt, Equity, Receivables, Inventory from Balance Sheet
Promoter shareholding percentage
Audit fees from notes

Approach: Use Gemini to extract structured data from specific sections
Test: Extract key financials from sample PDF

Phase 3: Red Flag Detection Engine (Week 3)
Milestone 3.1: Base Infrastructure (Day 8)
Files to create:

backend/app/red_flags/base.py - Base RedFlag class
backend/app/red_flags/__init__.py - Registry of all flags

Base class structure:
pythonclass RedFlag:
    id: int
    name: str
    category: str
    severity: str  # CRITICAL/HIGH/MEDIUM/LOW

    def check(self, data: dict) -> RedFlagResult:
        # Returns: is_triggered, evidence, page_refs
        pass
Milestone 3.2: Rule-Based Flags (Days 8-11)
Files to create (8 categories, 48 flags total):

backend/app/red_flags/auditor_flags.py - 8 flags
backend/app/red_flags/cashflow_flags.py - 8 flags (HIGHEST PRIORITY)
backend/app/red_flags/related_party_flags.py - 7 flags
backend/app/red_flags/promoter_flags.py - 6 flags
backend/app/red_flags/governance_flags.py - 7 flags
backend/app/red_flags/balance_sheet_flags.py - 7 flags
backend/app/red_flags/revenue_flags.py - 5 flags

Example implementation (Flag #9: Profit growing, CFO flat):
pythondef check_cfo_pat_divergence(data):
    cfo = data['cash_flow_from_operations']
    pat = data['profit_after_tax']

    cfo_growth = calculate_cagr(cfo, years=3)
    pat_growth = calculate_cagr(pat, years=3)
    cfo_pat_ratio = cfo[-1] / pat[-1] if pat[-1] > 0 else 0

    if pat_growth > 0.15 and cfo_growth < 0.05:
        return RedFlagResult(
            triggered=True,
            evidence=f"PAT growing at {pat_growth*100:.1f}% CAGR but CFO flat at {cfo_growth*100:.1f}%",
            severity="HIGH"
        )

    if cfo_pat_ratio < 0.5:
        return RedFlagResult(
            triggered=True,
            evidence=f"CFO/PAT ratio is {cfo_pat_ratio:.2f} (below 0.5 threshold)",
            severity="HIGH"
        )

    return RedFlagResult(triggered=False)
Test: Run each flag against mock financial data
Milestone 3.3: LLM-Based Flags (Days 11-12)
Files to create:

backend/app/red_flags/textual_flags.py - 6 LLM-powered flags

LLM flags:

Flag #49: MD&A tone defensive
Flag #50: Increased jargon
Flag #51: Declining disclosure
Flag #52: Risk factors expanding
Flag #53: Contradictions between text and numbers
Flag #54: Unusual audit language

Test: Run LLM flags on sample MD&A text
Milestone 3.4: Risk Scoring Engine (Day 12)
Files to create:

backend/app/scoring/risk_calculator.py - Calculate 0-100 risk score

Scoring formula:
Risk Score = Σ (Category Weight × Category Score)

Category Score = Σ (Flag Severity Points × Flag Triggered) / Max Points

Severity Points:
- CRITICAL: 25 points
- HIGH: 15 points
- MEDIUM: 8 points
- LOW: 3 points

Category Weights:
- Auditor: 20%
- Cash Flow: 18%
- Related Party: 15%
- Promoter: 15%
- Governance: 12%
- Balance Sheet: 10%
- Revenue: 5%
- Textual: 5%
Test: Calculate risk score for company with 5 triggered flags

Phase 4: Celery Background Jobs (Week 4)
Milestone 4.1: Celery Setup (Days 13-14)
Files to create:

backend/app/tasks/celery_app.py - Celery configuration
backend/app/tasks/analysis_tasks.py - Analysis job

Celery workflow:

User uploads PDF or searches company
API creates job in Redis queue
Celery worker picks up job
Runs full pipeline: extract → detect → check flags → score
Saves results to PostgreSQL
Sends WebSocket update to frontend

Test: Submit analysis job, verify it processes in background
Milestone 4.2: WebSocket Progress Updates (Day 14)
Files to create:

backend/app/api/v1/websocket.py - WebSocket endpoint

Progress updates:

"Uploading PDF..." (10%)
"Extracting text..." (30%)
"Detecting sections..." (50%)
"Checking red flags..." (70%)
"Calculating risk score..." (90%)
"Analysis complete!" (100%)

Test: Connect WebSocket client, submit job, see real-time updates

Phase 5: Analysis API (Week 4)
Milestone 5.1: Company Search (Day 15)
Files to create:

backend/app/api/v1/companies.py - Company endpoints
backend/app/services/company_service.py - Business logic

Endpoints:

GET /api/v1/companies/search?q=reliance - Search by name/code
GET /api/v1/companies/{id} - Get company details
GET /api/v1/companies/{id}/reports - List annual reports

Test: Search for "Reliance", get list of matching companies
Milestone 5.2: Analysis Endpoints (Days 15-16)
Files to create:

backend/app/api/v1/analyze.py - Analysis endpoints

Endpoints:

POST /api/v1/analyze/upload - Upload PDF file
POST /api/v1/analyze/company/{id} - Analyze by company ID
GET /api/v1/analyze/job/{job_id} - Get job status
GET /api/v1/reports/{report_id} - Get analysis results
GET /api/v1/reports/{report_id}/flags - Get triggered red flags
GET /api/v1/reports/{report_id}/export/pdf - Export as PDF

Test: Upload sample PDF via API, get analysis results

Phase 6: Frontend Foundation (Week 5)
Milestone 6.1: Next.js Setup (Days 17-18)
Commands:
bashcd D:\redflags
npx create-next-app@latest frontend
# Choose: TypeScript, Tailwind CSS, App Router, src/ directory: No
Install dependencies:
bashcd frontend
npm install @tanstack/react-query axios recharts d3 lucide-react
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card input dialog progress badge
Files to create:

frontend/lib/api/client.ts - Axios API client
frontend/lib/hooks/useAuth.ts - Authentication hook
frontend/lib/types/api.ts - TypeScript types
frontend/app/layout.tsx - Root layout with providers

Test: Run npm run dev, access http://localhost:3000
Milestone 6.2: Authentication Pages (Days 18-19)
Files to create:

frontend/app/(auth)/login/page.tsx - Login form
frontend/app/(auth)/signup/page.tsx - Signup form
frontend/components/forms/LoginForm.tsx - Reusable login component

Features:

Email/password login
JWT token storage in localStorage
Auto-redirect if already logged in
Error handling with toast notifications

Test: Signup new account, login, verify token stored
Milestone 6.3: Dashboard Layout (Day 19)
Files to create:

frontend/app/(dashboard)/layout.tsx - Shared layout
frontend/components/layout/Header.tsx - Top navigation
frontend/components/layout/Sidebar.tsx - Side menu
frontend/components/layout/Footer.tsx - Footer

Layout structure:

Header: Logo, search bar, notifications, user menu
Sidebar: Dashboard, Analyze, Portfolio, Watchlist, Learn, Settings
Main content area
Footer: Links, copyright

Test: Navigate between pages, verify layout consistency

Phase 7: Core Pages (Week 6)
Milestone 7.1: Landing Page (Days 20-21)
Files to create:

frontend/app/page.tsx - Landing page

Sections:

Hero - "Your AI Forensic Accountant"
Demo Preview - Sample analysis with risk score 67
Features - 8 feature cards with icons
Case Studies - Yes Bank, DHFL, Zee examples
Pricing - Free, Pro (Rs.599), Premium (Rs.1499)
Footer - Links, social media

Design: Clean, professional, trust-building. Use case studies prominently.
Test: Responsive design on mobile, tablet, desktop
Milestone 7.2: Dashboard Page (Day 21)
Files to create:

frontend/app/(dashboard)/dashboard/page.tsx

Components:

Recent analyses (last 10)
Quick stats: Reports this month, watchlist alerts
Recommended companies to analyze
Usage meter (Free: 2/3 reports used)

Test: Display mock recent analyses, click to view report
Milestone 7.3: Analysis Page (Days 22-23)
Files to create:

frontend/app/(dashboard)/analyze/page.tsx
frontend/components/forms/FileUpload.tsx - Drag-drop PDF upload
frontend/components/forms/CompanySearch.tsx - Autocomplete search
frontend/lib/hooks/useAnalysis.ts - Analysis submission hook

Features:

Tab 1: Search Company

Autocomplete search (API: /api/v1/companies/search)
Popular companies (Reliance, TCS, HDFC, etc.)
Click to analyze latest annual report


Tab 2: Upload PDF

Drag-and-drop area
File validation (PDF only, max 50MB)
Progress bar during upload


Analysis Options (Pro+):

 Multi-year trends
 Peer comparison


Submit Button

Creates background job
Shows WebSocket progress updates
Redirects to results page when complete



Test: Upload sample PDF, see progress bar, view results

Phase 8: Results Visualization (Week 7)
Milestone 8.1: Risk Score Components (Days 24-25)
Files to create:

frontend/components/analysis/RiskGauge.tsx - Circular gauge (0-100)
frontend/components/analysis/SpiderChart.tsx - 8-axis radar chart
frontend/components/analysis/CategoryBreakdown.tsx - Bar chart

Risk Gauge (Recharts):
tsx<RadialBarChart>
  <RadialBar
    dataKey="score"
    fill={score < 30 ? 'green' : score < 60 ? 'orange' : 'red'}
  />
  <text className="risk-score">{score}</text>
</RadialBarChart>
Spider Chart (Recharts):

8 axes: Auditor, Cash Flow, Related Party, Promoter, Governance, Balance Sheet, Revenue, Textual
Show category scores (0-100) on each axis
Fill area with gradient

Test: Display mock data with score 67, verify colors and labels
Milestone 8.2: Red Flag Cards (Day 25)
Files to create:

frontend/components/analysis/RedFlagCard.tsx
frontend/components/analysis/RedFlagList.tsx

Card structure:
tsx<Card className={severityColor}>
  <Badge>{severity}</Badge>
  <h3>{flagName}</h3>
  <p>{evidence}</p>
  <Button>View Details</Button>
  <span>Pages: 45-47</span>
</Card>
Severity colors:

CRITICAL: Red background, white text
HIGH: Orange background
MEDIUM: Yellow background
LOW: Blue background

Test: Display 12 triggered red flags, click to view details
Milestone 8.3: Results Page (Days 26-27)
Files to create:

frontend/app/(dashboard)/report/[id]/page.tsx

Layout:

Header

Company name, fiscal year, date analyzed
Export buttons (PDF, CSV)
Add to watchlist button


Risk Summary

Risk Gauge (left)
Spider Chart (right)
Risk level text: "ELEVATED RISK" with description


Category Breakdown

8 cards showing category scores
Click to filter red flags


Red Flags Section

Filter: All / Critical / High / Medium / Low
Sort: Severity / Category
List of triggered flags with evidence


Key Metrics

CFO/PAT ratio, Receivable days, Debt/Equity, etc.
3-year trend sparklines



Test: View full report, click flags to see details

Phase 9: Advanced Visualizations (Week 8)
Milestone 9.1: Related Party Spiderweb (Days 28-29)
Files to create:

frontend/components/analysis/Spiderweb.tsx - D3.js force-directed graph

Visualization:

Center node: Main company
Connected nodes: Related parties (subsidiaries, promoter entities, directors)
Edges: Transaction flows (thickness = amount, color = risk level)
Interactive: Drag nodes, hover for details, click for transaction list

D3.js implementation:
tsxuseEffect(() => {
  const simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links))
    .force("charge", d3.forceManyBody())
    .force("center", d3.forceCenter());

  // Render nodes and edges
}, [data]);
Test: Display spiderweb with 10 related parties, verify interactions
Milestone 9.2: Flag Detail Page (Day 29)
Files to create:

frontend/app/(dashboard)/report/[id]/flag/[flagId]/page.tsx

Content:

Flag description and severity
Why it matters (risk explanation)
Evidence with page references
Historical data (if multi-year)
Similar cases from fraud database
Recommendations

Test: Click flag card, view detailed explanation
Milestone 9.3: Trends Page (Days 30-31)
Files to create:

frontend/app/(dashboard)/report/[id]/trends/page.tsx (Pro+ feature)

Charts:

Risk score timeline (3-5 years)
Category score evolution
Key metric trends:

Promoter pledge %
CFO/PAT ratio
Receivable days
Debt/Equity ratio



Test: Display 3-year trends with line charts
Milestone 9.4: Peer Comparison Page (Day 31)
Files to create:

frontend/app/(dashboard)/report/[id]/peers/page.tsx (Pro+ feature)

Content:

Auto-suggested peers (same industry, similar size)
Side-by-side risk scores
Category comparison radar chart
Key metrics table
Flag count comparison

Test: Compare TCS vs Infosys vs Wipro

Phase 10: Portfolio & Watchlist (Week 9)
Milestone 10.1: Portfolio Scanner (Days 32-33)
Files to create:

frontend/app/(dashboard)/portfolio/page.tsx (Premium feature)
frontend/components/portfolio/PortfolioUpload.tsx - CSV upload
backend/app/api/v1/portfolio.py - Portfolio endpoints

Features:

Upload CSV from broker (Zerodha, Groww, Upstox format)
Parse holdings: Symbol, Quantity, Avg Price
Batch analyze all holdings
Display risk heatmap grid
Show alerts for high-risk stocks

Heatmap:
[HDFC: 22] [INFY: 18] [TCS: 25] [REL: 28]
[ICIC: 24] [AXIS: 35] [SBI: 21] [ZEE: 67!]
Test: Upload sample CSV with 15 holdings, view heatmap
Milestone 10.2: Watchlist (Days 33-34)
Files to create:

frontend/app/(dashboard)/watchlist/page.tsx
backend/app/api/v1/watchlist.py - Watchlist endpoints

Features:

Add company to watchlist
List watched companies with current risk scores
Show alerts (score changes >10, new flags, new AR filed)
Remove from watchlist

Alert system:

Free tier: No alerts
Pro tier: Weekly email digest
Premium tier: Real-time email + push notifications

Test: Add 5 companies to watchlist, verify alerts

Phase 11: Learning & Settings (Week 10)
Milestone 11.1: Fraud Database (Days 35-36)
Files to create:

frontend/app/(dashboard)/learn/page.tsx
backend/scripts/seed_fraud_cases.py - Seed 50+ fraud cases

Content:

Featured Case Study

Yes Bank (2020, -98.8% decline)
Timeline with red flags
What investors should have noticed


All Cases Table

Company, Year, Decline %, Primary Flags
Filter by sector
Click to view full case study


Pattern Matching

"Check if your stock matches fraud patterns"
Enter company name
Show similarity score with historical frauds



Fraud cases to include:

Yes Bank, DHFL, Zee, Satyam, PC Jeweller, Vakrangee, Manpasand, Gitanjali Gems, IL&FS, Fortis Healthcare, etc.

Test: Browse fraud cases, match patterns
Milestone 11.2: Settings Page (Days 36-37)
Files to create:

frontend/app/(dashboard)/settings/page.tsx

Sections:

Profile

Name, email, password change
Profile picture upload


Subscription

Current plan (Free/Pro/Premium)
Usage this month
Upgrade buttons with Razorpay integration


Notification Preferences

Email alerts for watchlist
Weekly digest
Push notifications (browser)
Feature announcements


Data & Privacy

Download my data
Delete analysis history


Danger Zone

Delete account (with confirmation)



Test: Update profile, change notification settings

Phase 12: Docker & Deployment (Week 11)
Milestone 12.1: Docker Compose (Days 38-39)
Files to create:

docker/docker-compose.yml - Local development
docker/Dockerfile.frontend - Next.js container
docker/Dockerfile.backend - FastAPI container

docker-compose.yml:
yamlversion: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: redflags
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build:
      context: ../backend
      dockerfile: ../docker/Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/redflags
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis
    volumes:
      - ../backend:/app

  celery:
    build:
      context: ../backend
      dockerfile: ../docker/Dockerfile.backend
    command: celery -A app.tasks.celery_app worker --loglevel=info
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/redflags
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis

  frontend:
    build:
      context: ../frontend
      dockerfile: ../docker/Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    depends_on:
      - backend
    volumes:
      - ../frontend:/app
      - /app/node_modules

volumes:
  postgres_data:
Test: Run docker-compose up, access app at http://localhost:3000
Milestone 12.2: Production Deployment (Days 39-40)
Deployment options:
Option 1: DigitalOcean (Recommended for Docker)

Create Droplet ($12/month for 2GB RAM)
Install Docker
Copy docker-compose.prod.yml to server
Set environment variables
Run docker-compose -f docker-compose.prod.yml up -d
Setup nginx reverse proxy
Get SSL certificate (Let's Encrypt)

Option 2: Railway (Easier for beginners)

Connect GitHub repo
Deploy backend from backend/ folder
Deploy frontend from frontend/ folder
Add PostgreSQL and Redis addons
Set environment variables

Option 3: AWS/GCP (Most scalable)

Use ECS (AWS) or Cloud Run (GCP)
Upload Docker images to ECR/GCR
Setup RDS PostgreSQL and ElastiCache Redis
Configure load balancer and auto-scaling

Test: Deploy to staging environment, run end-to-end tests

Phase 13: Real Data Integration (Week 12)
Milestone 13.1: BSE/NSE Company Data (Days 41-42)
Files to create:

backend/scripts/seed_companies.py - Fetch and seed NIFTY 500

Data sources:

NSE Website: https://www.nseindia.com/

Download NIFTY 500 CSV
Contains: Symbol, Company Name, Industry, ISIN


BSE Website: https://www.bseindia.com/

Download listed companies CSV
Contains: BSE Code, Company Name, Market Cap


Manual mapping: Match NSE symbols to BSE codes

Script logic:
pythonimport pandas as pd
from app.database import SessionLocal
from app.models.company import Company

def seed_companies():
    # Load NIFTY 500 CSV
    df = pd.read_csv('nifty500.csv')

    # Iterate and insert
    for _, row in df.iterrows():
        company = Company(
            name=row['Company Name'],
            nse_symbol=row['Symbol'],
            industry=row['Industry'],
            isin=row['ISIN'],
            is_nifty_500=True
        )
        db.add(company)

    db.commit()
Test: Run seed script, verify 500 companies in database
Milestone 13.2: Annual Report Fetching (Days 42-43)
Files to create:

backend/scripts/fetch_annual_reports.py - Download PDFs

Sources:

Company websites: Investor Relations section
BSE: https://www.bseindia.com/corporates/annualreports.aspx
NSE: Company filings section
SEBI website: https://www.sebi.gov.in/

Approach:

Build web scraper using BeautifulSoup
For top 100 companies, download last 3 years
Upload to R2 storage
Insert records in annual_reports table

Test: Download 10 sample annual reports
Milestone 13.3: Pre-Compute Cache (Days 43-44)
Files to create:

backend/scripts/pre_compute_cache.py - Analyze NIFTY 500

Strategy:

Analyze all NIFTY 500 companies (500 × Rs.6 = Rs.3,000 one-time cost)
Store results in database
When user searches, return cached result (Rs.0 cost)
Refresh cache quarterly when new ARs are filed

Optimization:

Analyze in parallel (10 workers)
Estimated time: 500 reports ÷ 10 workers × 2 min/report = 100 minutes

Test: Pre-analyze 50 companies, verify results cached

Phase 14: Polish & Testing (Week 13)
Milestone 14.1: Mobile Responsiveness (Days 45-46)
Files to update:

All frontend pages and components

Responsive design checklist:

 Landing page works on 375px (iPhone SE)
 Dashboard sidebar collapses to hamburger menu
 Analysis page file upload works on mobile
 Risk gauge scales down properly
 Red flag cards stack vertically
 Tables become scrollable
 Spiderweb graph is touch-enabled

Test: Use Chrome DevTools device emulation, test on real phone
Milestone 14.2: PWA Support (Day 46)
Files to create:

frontend/public/manifest.json - PWA manifest
frontend/public/sw.js - Service worker (optional)
frontend/app/layout.tsx - Add manifest link

PWA features:

Install to home screen
Offline support (view cached reports)
Push notifications (for alerts)

Test: Install app on Android phone, test offline mode
Milestone 14.3: Error Handling (Days 47-48)
Files to update:

All API endpoints (backend)
All React components (frontend)

Backend:

Validate all inputs with Pydantic
Return proper HTTP status codes
Log errors to Sentry
Handle PDF extraction failures gracefully

Frontend:

Display user-friendly error messages
Add error boundaries for React components
Show retry buttons
Fallback UI for loading states

Test: Trigger errors (invalid PDF, API down), verify handling
Milestone 14.4: End-to-End Testing (Days 48-49)
Test scenarios:

User Journey 1: Signup → Search company → View report → Add to watchlist
User Journey 2: Login → Upload PDF → Wait for analysis → Export results
User Journey 3: Dashboard → View recent reports → Click flag → See details
User Journey 4: Portfolio → Upload CSV → View heatmap → Click high-risk stock
User Journey 5: Learn → Browse fraud cases → Pattern match → View similar stock

Tools:

Playwright (frontend E2E)
pytest (backend unit tests)
Postman collections (API tests)

Test: Run full test suite, achieve >80% coverage

Phase 15: Launch Preparation (Week 14)
Milestone 15.1: Payment Integration (Days 50-51)
Files to create:

frontend/components/subscription/PricingCard.tsx
frontend/app/checkout/page.tsx
backend/app/api/v1/payments.py - Razorpay integration

Razorpay flow:

User clicks "Upgrade to Pro"
Backend creates Razorpay order
Frontend shows Razorpay checkout modal
User pays with card/UPI
Razorpay webhook confirms payment
Backend updates user subscription_tier
User gets Pro access immediately

Test: Complete payment flow in test mode
Milestone 15.2: Email Notifications (Days 51-52)
Files to create:

backend/app/services/email_service.py - SendGrid integration
backend/app/templates/emails/ - Email templates

Email types:

Welcome email (signup)
Analysis complete notification
Watchlist alert (Pro/Premium)
Weekly digest (Pro/Premium)
Payment receipt
Password reset

Test: Trigger each email type, verify delivery
Milestone 15.3: Documentation (Days 52-53)
Files to create:

README.md - Project overview
docs/SETUP.md - Local setup guide
docs/DEPLOYMENT.md - Deployment guide
docs/API.md - API documentation
docs/ARCHITECTURE.md - System architecture

README structure:
markdown# RedFlag AI

AI-powered forensic accounting scanner for annual reports.

## Features
- Instant PDF analysis
- 54 red flag detection
- Risk scoring (0-100)
- Portfolio scanner
- Watchlist & alerts

## Tech Stack
- Frontend: Next.js 14, Tailwind, shadcn/ui
- Backend: Python FastAPI, Celery
- Database: PostgreSQL, Redis
- AI: Google Gemini

## Setup
See [SETUP.md](docs/SETUP.md)

## API Documentation
See [API.md](docs/API.md)
Test: Follow setup guide from scratch, verify it works
Milestone 15.4: Marketing Site Polish (Days 53-54)
Landing page improvements:

Add testimonials (mock for now)
Add trust badges (Y Combinator, Product Hunt, etc. - placeholder)
Add demo video (record screencast)
Add FAQ section
Add live chat widget (optional)
Optimize SEO meta tags
Add Google Analytics

Test: Check page speed (target: <3s load time)

Critical Files for Implementation
The 5 most important files to implement well:

backend/app/pdf_pipeline/extractor.py - Core PDF extraction logic
backend/app/red_flags/cashflow_flags.py - Highest-weight red flag category
backend/app/tasks/analysis_tasks.py - Orchestrates entire pipeline
frontend/components/analysis/RiskGauge.tsx - Main visual component
frontend/app/(dashboard)/analyze/page.tsx - Primary user interaction point

Testing Checkpoints
After each phase:

Week 1: Backend API responds at /docs
Week 2: Can extract text from sample PDF
Week 3: Red flags detect correctly on mock data
Week 4: Background job completes successfully
Week 5: Frontend displays risk score
Week 6: Can upload PDF and see results
Week 7: All visualizations render correctly
Week 8: Spiderweb graph is interactive
Week 9: Portfolio scanner works with CSV
Week 10: Fraud database displays cases
Week 11: Docker deployment successful
Week 12: Real company data integrated
Week 13: Mobile-responsive and tested
Week 14: Production-ready with payments

Common Pitfalls for Beginners

Forgetting to activate Python virtual environment - Always run venv\Scripts\activate before pip install
Port conflicts - If 8000 is taken, use uvicorn main:app --port 8001
CORS errors - Add frontend URL to CORS middleware
Database connection issues - Check DATABASE_URL in .env
PDF extraction fails - Some PDFs are image-based, need OCR
LLM costs accumulating - Cache NIFTY 500 to avoid repeated analysis
Docker volumes not syncing - Use absolute paths in docker-compose
Next.js API routes not working - Use app router, not pages router
Celery not picking up jobs - Ensure Redis is running and connected
Vercel build failing - Check environment variables are set

Environment Variables Checklist
Backend (.env):

 DATABASE_URL (Supabase PostgreSQL)
 REDIS_URL (Upstash)
 GEMINI_API_KEY
 R2_ACCESS_KEY_ID
 R2_SECRET_ACCESS_KEY
 JWT_SECRET_KEY
 RAZORPAY_KEY_ID

Frontend (.env.local):

 NEXT_PUBLIC_API_URL
 NEXT_PUBLIC_WS_URL
 NEXT_PUBLIC_RAZORPAY_KEY_ID

Resource Recommendations
Tutorials:

FastAPI: https://fastapi.tiangolo.com/tutorial/
Next.js 14: https://nextjs.org/learn
SQLAlchemy: https://docs.sqlalchemy.org/en/20/tutorial/
Celery: https://docs.celeryq.dev/en/stable/getting-started/
D3.js: https://observablehq.com/@d3/gallery

Documentation:

Gemini API: https://ai.google.dev/docs
PyMuPDF: https://pymupdf.readthedocs.io/
Tailwind CSS: https://tailwindcss.com/docs
shadcn/ui: https://ui.shadcn.com/

Communities:

r/FastAPI (Reddit)
Next.js Discord
Stack Overflow

Success Metrics
MVP (Week 8):

Can analyze 1 PDF in 60 seconds
Detects at least 20/54 red flags correctly
Frontend displays risk score and top 10 flags
Basic authentication works

Beta (Week 14):

NIFTY 500 companies pre-cached
Portfolio scanner works
Payments integrated
Mobile-responsive
Real users testing

Launch (Week 16):

100+ annual reports analyzed
50+ fraud cases in database
Deployment on production
Marketing site live

Next Steps After Plan Approval

Create all folder structures
Setup backend Python environment
Install dependencies
Create database models
Build PDF extraction pipeline
Implement red flag detection
Build frontend pages
Integrate everything
Test end-to-end
Deploy to production

Cost Summary
Development (Local):

API costs: ~Rs.500 (testing)
Total: Rs.500

Production (First Month):

Server (DigitalOcean Droplet): Rs.960 ($12)
Database (Supabase): Rs.2,000
Redis (Upstash): Rs.500
Storage (Cloudflare R2): Rs.500
Pre-compute NIFTY 500: Rs.3,000 (one-time)
Per-analysis cost: Rs.2-3 (cached)
Total: ~Rs.7,000 first month, ~Rs.4,000 recurring

Comparison:

Original plan (Vercel + Railway): ~Rs.10,500/month
Docker approach (DigitalOcean): ~Rs.4,000/month
Savings: 60% cheaper

Timeline Summary

Phase 0: Environment setup (2 days)
Phase 1-5: Backend (4 weeks)
Phase 6-11: Frontend (6 weeks)
Phase 12-13: Deployment & data (2 weeks)
Phase 14-15: Polish & launch (2 weeks)
Total: 14 weeks (~3.5 months)

Verification Steps
Before marking plan complete:

 All API keys obtained
 Development environment setup
 Docker Desktop running
 Project structure understood
 Tech stack confirmed
 Timeline realistic for novice developer
 User questions answered


Ready to start building! Once you approve this plan, we'll begin with Phase 0: Environment Setup.