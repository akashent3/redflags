# RedFlags AI - Complete Architecture Documentation

> **Last Updated:** February 7, 2026  
> **Version:** 1.0.0  
> **Purpose:** Comprehensive architecture reference for development and maintenance

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Backend Architecture](#backend-architecture)
5. [Frontend Architecture](#frontend-architecture)
6. [Database Schema](#database-schema)
7. [Red Flag Detection System](#red-flag-detection-system)
8. [Data Flow & Workflows](#data-flow--workflows)
9. [Background Jobs](#background-jobs)
10. [External Integrations](#external-integrations)
11. [Setup & Deployment](#setup--deployment)
12. [API Reference](#api-reference)

---

## System Overview

**RedFlags AI** is a forensic accounting scanner that analyzes corporate annual reports using AI to detect financial red flags. The application targets retail investors and provides comprehensive risk assessment for Indian listed companies.

### Key Features

- **PDF Analysis**: Upload annual reports or search by company name
- **54 Red Flag Checks**: Across 8 categories (Auditor, Cash Flow, Related Party, Promoter, Governance, Balance Sheet, Revenue, Textual)
- **Risk Scoring**: 0-100 risk score with category breakdowns
- **Portfolio Scanner**: Analyze entire portfolio from broker CSV (Premium)
- **Watchlist Alerts**: Real-time monitoring with email/push notifications
- **Fraud Pattern Matching**: Compare companies against historical fraud cases
- **Multi-tier Subscription**: Free (3 reports/month), Pro (unlimited + trends), Premium (portfolio + real-time alerts)

### Architecture Pattern

- **Frontend**: Next.js 14 (App Router) with TypeScript
- **Backend**: FastAPI (Python) with async/await
- **Database**: PostgreSQL (via Supabase)
- **Cache/Queue**: Redis (via Upstash)
- **Storage**: Cloudflare R2 for PDFs
- **Background Jobs**: Celery with Redis broker
- **AI Processing**: Google Gemini API

---

## Technology Stack

### Frontend Stack

| Technology | Purpose | Version |
|------------|---------|---------|
| Next.js | React framework with App Router | 14.x |
| TypeScript | Type safety | 5.x |
| Tailwind CSS | Styling framework | 3.x |
| shadcn/ui | UI component library | Latest |
| Recharts | Charts and visualizations | 2.x |
| D3.js | Network graphs (spiderweb) | 7.x |
| Axios | HTTP client | 1.x |
| React Query | Data fetching and caching | 5.x |

### Backend Stack

| Technology | Purpose | Version |
|------------|---------|---------|
| FastAPI | Web framework | 0.109+ |
| Python | Programming language | 3.11 |
| SQLAlchemy | ORM | 2.0+ |
| Alembic | Database migrations | 1.13+ |
| Celery | Background task queue | 5.3+ |
| Redis | Cache and message broker | 7.x |
| PyMuPDF | PDF text extraction | 1.23+ |
| Surya OCR | Scanned PDF processing | Latest |
| google-generativeai | Gemini API client | Latest |
| pandas | CSV processing | 2.0+ |
| sib-api-v3-sdk | Brevo email service | 7.6+ |
| pywebpush | Web push notifications | 1.14+ |

### Infrastructure

| Service | Purpose | Provider |
|---------|---------|----------|
| Database | PostgreSQL 15 | Supabase |
| Cache/Queue | Redis | Upstash |
| Storage | Object storage for PDFs | Cloudflare R2 |
| Email | Transactional emails | Brevo |
| Deployment | Docker containers | Local/Cloud |

---

## Project Structure

```
D:\redflags\
├── frontend/                    # Next.js 14 application
│   ├── app/                     # App router pages
│   │   ├── (auth)/             # Auth pages (login, signup)
│   │   ├── (dashboard)/        # Protected dashboard pages
│   │   ├── layout.tsx          # Root layout
│   │   └── page.tsx            # Landing page
│   ├── components/             # React components
│   │   ├── analysis/           # Analysis visualization components
│   │   ├── forms/              # Form components
│   │   ├── layout/             # Layout components
│   │   └── portfolio/          # Portfolio components
│   ├── lib/                    # Utilities and helpers
│   │   ├── api/                # API client
│   │   ├── hooks/              # Custom React hooks
│   │   ├── types/              # TypeScript types
│   │   └── utils/              # Utility functions
│   └── public/                 # Static assets
│
├── backend/                    # Python FastAPI
│   ├── app/
│   │   ├── api/v1/            # REST API endpoints
│   │   │   ├── analysis.py    # Analysis endpoints
│   │   │   ├── auth.py        # Authentication
│   │   │   ├── companies.py   # Company search
│   │   │   ├── fraud_cases.py # Fraud database
│   │   │   ├── portfolio.py   # Portfolio scanner
│   │   │   ├── reports.py     # Report viewing
│   │   │   ├── users.py       # User management
│   │   │   └── watchlist.py   # Watchlist & alerts
│   │   ├── models/            # SQLAlchemy models
│   │   │   ├── user.py        # User & subscription
│   │   │   ├── company.py     # Companies
│   │   │   ├── annual_report.py # Annual reports
│   │   │   ├── analysis_result.py # Analysis results
│   │   │   ├── red_flag.py    # Red flags
│   │   │   ├── watchlist.py   # Watchlist items/alerts
│   │   │   └── portfolio.py   # Portfolios & holdings
│   │   ├── pdf_pipeline/      # PDF processing
│   │   │   ├── extractor.py   # Text extraction
│   │   │   ├── ocr_fallback.py # OCR processing
│   │   │   ├── section_detector.py # Section detection
│   │   │   └── data_extractor.py # Financial data extraction
│   │   ├── red_flags/         # 54 red flag detectors
│   │   │   ├── base.py        # Base classes
│   │   │   ├── registry.py    # Flag registry
│   │   │   ├── auditor_flags.py # 8 auditor flags
│   │   │   ├── cashflow_flags.py # 8 cash flow flags
│   │   │   ├── related_party_flags.py # 7 RPT flags
│   │   │   ├── promoter_flags.py # 6 promoter flags
│   │   │   ├── governance_flags.py # 7 governance flags
│   │   │   ├── balance_sheet_flags.py # 7 BS flags
│   │   │   ├── revenue_flags.py # 5 revenue flags
│   │   │   └── textual_flags.py # 6 LLM-based flags
│   │   ├── llm/               # Gemini integration
│   │   │   ├── gemini_client.py # API wrapper
│   │   │   └── prompts.py     # Prompt templates
│   │   ├── scoring/           # Risk scoring
│   │   │   └── risk_calculator.py # Score calculation
│   │   ├── services/          # Business logic
│   │   │   ├── portfolio_service.py # CSV parsing
│   │   │   ├── email_service.py # Brevo integration
│   │   │   └── push_service.py # Web push
│   │   ├── tasks/             # Celery background jobs
│   │   │   ├── analysis_tasks.py # PDF analysis
│   │   │   ├── watchlist_tasks.py # Alert checking
│   │   │   └── export_tasks.py # Data export
│   │   ├── storage/           # R2 storage
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── main.py            # FastAPI app
│   │   ├── config.py          # Configuration
│   │   ├── database.py        # DB connection
│   │   └── celery_app.py      # Celery config
│   ├── alembic/               # Database migrations
│   ├── data/                  # Seed data
│   │   └── fraud_cases.json   # 6 fraud cases
│   ├── tests/                 # Test files
│   └── requirements.txt       # Python dependencies
│
├── docker/                    # Docker configuration
├── scripts/                   # Setup & seed scripts
└── docs/                      # Documentation
    └── plan.md                # Master implementation plan
```

---

## Backend Architecture

### Core Components

#### 1. FastAPI Application ([main.py](file:///d:/redflags/backend/app/main.py))

```python
# Entry point with CORS, error handling, and API routing
app = FastAPI(title="RedFlag AI API", version="1.0.0")
app.include_router(api_router, prefix="/api/v1")
```

**Key Features:**
- CORS middleware for frontend communication
- Global exception handler
- Health check endpoint
- Auto-generated OpenAPI docs at `/docs`

#### 2. API Routers ([api/v1/](file:///d:/redflags/backend/app/api/v1/__init__.py))

8 modular routers organized by feature:

| Router | Prefix | Endpoints | Purpose |
|--------|--------|-----------|---------|
| **auth** | `/auth` | 4 | Signup, login, refresh token, get current user |
| **companies** | `/companies` | 3 | Search companies, get details, list reports |
| **analysis** | `/analysis` | 3 | Upload PDF, analyze by company, check job status |
| **reports** | `/reports` | 4 | View results, get flags, export PDF/CSV |
| **portfolio** | `/portfolio` | 4 | Upload CSV, list portfolios, view details, delete |
| **watchlist** | `/watchlist` | 8 | Add/remove companies, manage alerts, preferences, push subscriptions |
| **fraud_cases** | `/fraud-cases` | 4 | List cases, get details, pattern matching, get patterns |
| **users** | `/users` | 5 | Profile, update, change password, delete account, export data |

**Total: 35 API endpoints**

#### 3. Database Models ([models/](file:///d:/redflags/backend/app/models/__init__.py))

8 SQLAlchemy models with relationships:

```mermaid
erDiagram
    User ||--o{ WatchlistItem : has
    User ||--o{ Portfolio : owns
    User ||--o| NotificationPreference : has
    Company ||--o{ AnnualReport : has
    Company ||--o{ WatchlistItem : tracked_in
    AnnualReport ||--o{ AnalysisResult : generates
    AnalysisResult ||--o{ RedFlag : contains
    WatchlistItem ||--o{ WatchlistAlert : triggers
    Portfolio ||--o{ Holding : contains
    Company ||--o{ Holding : referenced_in
```

**Key Models:**

- **User**: Authentication, subscription tier (FREE/PRO/PREMIUM), usage limits
- **Company**: BSE/NSE companies, NIFTY 500 data, industry/sector
- **AnnualReport**: PDF metadata, fiscal year, R2 storage URL
- **AnalysisResult**: Risk score, category scores, summary
- **RedFlag**: 54 flags with triggered status, evidence, severity
- **WatchlistItem**: User's tracked companies with alert settings
- **WatchlistAlert**: Generated alerts with severity levels
- **Portfolio**: User portfolios with risk metrics
- **Holding**: Individual stock holdings with risk scores

#### 4. PDF Processing Pipeline ([pdf_pipeline/](file:///d:/redflags/backend/app/pdf_pipeline/))

Multi-stage extraction process:

```mermaid
graph LR
    A[PDF Upload] --> B[R2 Storage]
    B --> C{Text Extraction}
    C -->|Success| D[PyMuPDF]
    C -->|Garbled| E[Surya OCR]
    E -->|Fail| F[Google Vision API]
    D --> G[Section Detection]
    E --> G
    F --> G
    G --> H[Gemini LLM]
    H --> I[Financial Data Extraction]
    I --> J[Structured Data]
```

**Components:**

- **extractor.py**: Main extraction orchestrator
- **ocr_fallback.py**: Surya OCR for scanned PDFs
- **section_detector.py**: LLM-based section identification
- **data_extractor.py**: Extract financial metrics from tables

**Extracted Sections:**
- Auditor's Report
- Cash Flow Statement
- Balance Sheet
- Profit & Loss Statement
- Notes to Accounts
- Director's Report
- Corporate Governance Report

#### 5. Red Flag Detection System ([red_flags/](file:///d:/redflags/backend/app/red_flags/))

54 detectors across 8 categories with centralized registry:

**Architecture:**

```python
# Base class for all detectors
class RedFlagBase:
    def check(self, data: Dict) -> RedFlagResult:
        # Returns: is_triggered, evidence, confidence, page_refs
        pass
```

**Registry Pattern:**

```python
# Global singleton registry
flag_registry = FlagRegistry()

# Auto-registration on import
flag_registry.register(AuditorChangedFlag())
flag_registry.register(CFOPATDivergenceFlag())
# ... 52 more flags
```

**Detection Methods:**
- **Rule-based** (48 flags): Mathematical calculations on financial data
- **LLM-based** (6 flags): Gemini analysis of textual content
- **Hybrid**: Combination of both approaches

#### 6. Risk Scoring Engine ([scoring/risk_calculator.py](file:///d:/redflags/backend/app/scoring/))

Weighted scoring algorithm:

```
Risk Score (0-100) = Σ (Category Weight × Category Score)

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
```

#### 7. Background Jobs ([tasks/](file:///d:/redflags/backend/app/tasks/))

Celery tasks for async processing:

- **analysis_tasks.py**: PDF analysis pipeline (10-60 seconds)
- **watchlist_tasks.py**: Daily alert checking, weekly digest
- **export_tasks.py**: User data export to ZIP

#### 8. External Services ([services/](file:///d:/redflags/backend/app/services/))

- **portfolio_service.py**: CSV parsing for Zerodha/Groww/Upstox
- **email_service.py**: Brevo API integration for transactional emails
- **push_service.py**: Web Push API with VAPID authentication

---

## Frontend Architecture

### Page Structure

12 pages organized in route groups:

#### Public Pages

| Page | Route | Purpose |
|------|-------|---------|
| Landing | `/` | Hero, features, pricing, case studies |

#### Auth Pages (`(auth)/`)

| Page | Route | Purpose |
|------|-------|---------|
| Login | `/login` | Email/password authentication |
| Signup | `/signup` | Account creation |

#### Dashboard Pages (`(dashboard)/`)

| Page | Route | Tier | Purpose |
|------|-------|------|---------|
| Dashboard | `/dashboard` | All | Recent analyses, quick stats |
| Analyze | `/analyze` | All | Upload PDF or search company |
| Report | `/report/[id]` | All | View analysis results |
| Portfolio | `/portfolio` | Premium | Upload broker CSV, risk heatmap |
| Watchlist | `/watchlist` | All | Track companies, view alerts |
| Learn | `/learn` | All | Fraud case studies, pattern matching |
| Settings | `/settings` | All | Profile, subscription, preferences |

**Additional Report Pages:**
- `/report/[id]/flag/[flagId]` - Detailed flag explanation
- `/report/[id]/trends` - Multi-year trends (Pro+)
- `/report/[id]/peers` - Peer comparison (Pro+)

### Component Architecture

```
components/
├── analysis/              # Visualization components
│   ├── RiskGauge.tsx     # Circular 0-100 gauge
│   ├── SpiderChart.tsx   # 8-axis radar chart
│   ├── CategoryBreakdown.tsx # Bar chart
│   ├── RedFlagCard.tsx   # Individual flag display
│   ├── RedFlagList.tsx   # Filterable flag list
│   └── Spiderweb.tsx     # D3 force-directed graph (RPT)
├── forms/                 # Input components
│   ├── FileUpload.tsx    # Drag-drop PDF upload
│   ├── CompanySearch.tsx # Autocomplete search
│   └── LoginForm.tsx     # Auth forms
├── layout/                # Layout components
│   ├── Header.tsx        # Top navigation
│   ├── Sidebar.tsx       # Side menu
│   └── Footer.tsx        # Footer
└── portfolio/             # Portfolio components
    ├── PortfolioUpload.tsx # CSV upload
    └── RiskHeatmap.tsx   # Grid visualization
```

### State Management

- **React Context**: User authentication state
- **React Query (SWR)**: Server state caching and synchronization
- **Local State**: Component-level state with useState/useReducer

### Data Fetching Pattern

```typescript
// Custom hook example
export function useAnalysis(reportId: string) {
  return useQuery({
    queryKey: ['analysis', reportId],
    queryFn: () => apiClient.get(`/reports/${reportId}`),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
```

---

## Database Schema

### Tables Overview

10 tables with proper indexing and foreign keys:

#### 1. users

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| email | VARCHAR(255) | UNIQUE, NOT NULL, INDEX |
| hashed_password | VARCHAR(255) | NOT NULL |
| full_name | VARCHAR(255) | |
| subscription_tier | ENUM | DEFAULT 'free' |
| subscription_active | BOOLEAN | DEFAULT true |
| reports_used_this_month | INTEGER | DEFAULT 0 |
| reports_limit | INTEGER | DEFAULT 3 |
| created_at | TIMESTAMP | NOT NULL |
| is_active | BOOLEAN | DEFAULT true |

#### 2. companies

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| name | VARCHAR(255) | NOT NULL, INDEX |
| bse_code | VARCHAR(10) | INDEX |
| nse_symbol | VARCHAR(20) | INDEX |
| isin | VARCHAR(12) | UNIQUE |
| industry | VARCHAR(100) | |
| sector | VARCHAR(100) | |
| market_cap_cr | DECIMAL(20,2) | |
| is_nifty_50 | BOOLEAN | DEFAULT false |
| is_nifty_500 | BOOLEAN | DEFAULT false, INDEX |

#### 3. annual_reports

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| company_id | UUID | FK → companies |
| fiscal_year | VARCHAR(10) | NOT NULL |
| file_url | VARCHAR(512) | R2 storage URL |
| file_size_mb | DECIMAL(10,2) | |
| page_count | INTEGER | |
| uploaded_at | TIMESTAMP | |

#### 4. analysis_results

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| annual_report_id | UUID | FK → annual_reports |
| user_id | UUID | FK → users |
| risk_score | INTEGER | 0-100 |
| risk_level | VARCHAR(20) | LOW/MEDIUM/HIGH/CRITICAL |
| auditor_score | INTEGER | 0-100 |
| cashflow_score | INTEGER | 0-100 |
| related_party_score | INTEGER | 0-100 |
| promoter_score | INTEGER | 0-100 |
| governance_score | INTEGER | 0-100 |
| balance_sheet_score | INTEGER | 0-100 |
| revenue_score | INTEGER | 0-100 |
| textual_score | INTEGER | 0-100 |
| flags_triggered_count | INTEGER | |
| analyzed_at | TIMESTAMP | |

#### 5. red_flags

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| analysis_result_id | UUID | FK → analysis_results |
| flag_number | INTEGER | 1-54 |
| flag_name | VARCHAR(200) | |
| category | ENUM | FlagCategory |
| severity | ENUM | FlagSeverity |
| is_triggered | BOOLEAN | |
| confidence_score | DECIMAL(5,2) | 0-100 |
| evidence_text | TEXT | |
| page_references | INTEGER[] | Array of page numbers |

#### 6. watchlist_items

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| user_id | UUID | FK → users |
| company_id | UUID | FK → companies |
| added_at | TIMESTAMP | |
| alert_enabled | BOOLEAN | DEFAULT true |
| last_known_risk_score | INTEGER | |
| last_checked_at | TIMESTAMP | |

**UNIQUE(user_id, company_id)**

#### 7. watchlist_alerts

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| watchlist_item_id | UUID | FK → watchlist_items |
| alert_type | ENUM | SCORE_CHANGE/NEW_FLAGS/NEW_REPORT |
| severity | ENUM | INFO/WARNING/CRITICAL |
| message | TEXT | |
| previous_risk_score | INTEGER | |
| current_risk_score | INTEGER | |
| score_change | INTEGER | |
| is_read | BOOLEAN | DEFAULT false |
| created_at | TIMESTAMP | |

#### 8. notification_preferences

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| user_id | UUID | FK → users, UNIQUE |
| email_alerts_enabled | BOOLEAN | DEFAULT true |
| weekly_digest_enabled | BOOLEAN | DEFAULT true |
| push_notifications_enabled | BOOLEAN | DEFAULT false |
| push_subscription_endpoint | VARCHAR(512) | |
| push_subscription_keys | TEXT | JSON |
| alert_frequency | ENUM | real_time/daily/weekly/none |

#### 9. portfolios

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| user_id | UUID | FK → users |
| name | VARCHAR(200) | DEFAULT "My Portfolio" |
| total_investment | DECIMAL(15,2) | |
| average_risk_score | FLOAT | |
| high_risk_count | INTEGER | |
| created_at | TIMESTAMP | |

#### 10. holdings

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| portfolio_id | UUID | FK → portfolios |
| company_id | UUID | FK → companies, NULLABLE |
| symbol | VARCHAR(50) | |
| company_name | VARCHAR(300) | |
| quantity | INTEGER | |
| avg_price | DECIMAL(15,2) | |
| investment_value | DECIMAL(15,2) | |
| risk_score | INTEGER | |
| risk_level | VARCHAR(20) | |

---

## Red Flag Detection System

### 54 Red Flags Across 8 Categories

#### Category 1: Auditor Flags (8 flags)

| # | Flag Name | Severity | Detection Method |
|---|-----------|----------|------------------|
| 1 | Auditor changed in last 2 years | HIGH | Rule-based |
| 2 | Qualified audit opinion | CRITICAL | Text matching |
| 3 | Going concern warning | CRITICAL | Text matching |
| 4 | Audit fees declining | MEDIUM | Calculation |
| 5 | Non-Big 4 auditor for large cap | LOW | Rule-based |
| 6 | Audit committee issues | HIGH | LLM analysis |
| 7 | Delayed audit report | MEDIUM | Date comparison |
| 8 | Emphasis of matter paragraph | MEDIUM | Text matching |

#### Category 2: Cash Flow Flags (8 flags) - **HIGHEST PRIORITY**

| # | Flag Name | Severity | Detection Method |
|---|-----------|----------|------------------|
| 9 | Profit growing but CFO flat/declining | HIGH | CAGR comparison |
| 10 | CFO/PAT ratio < 0.5 | HIGH | Ratio calculation |
| 11 | Negative CFO for 2+ years | CRITICAL | Trend analysis |
| 12 | Large gap between EBIT and CFO | HIGH | Difference calculation |
| 13 | Increasing working capital needs | MEDIUM | Trend analysis |
| 14 | Free cash flow negative | MEDIUM | Calculation |
| 15 | CFO volatility high | MEDIUM | Standard deviation |
| 16 | Cash conversion cycle lengthening | MEDIUM | Trend analysis |

#### Category 3: Related Party Transactions (7 flags)

| # | Flag Name | Severity | Detection Method |
|---|-----------|----------|------------------|
| 17 | RPT > 10% of revenue | HIGH | Percentage calculation |
| 18 | RPT growing faster than revenue | HIGH | Growth rate comparison |
| 19 | Loans to related parties | CRITICAL | Text + amount extraction |
| 20 | Transactions with promoter entities | MEDIUM | Entity matching |
| 21 | Non-arm's length pricing | HIGH | LLM analysis |
| 22 | Complex RPT structure | MEDIUM | Network analysis |
| 23 | Undisclosed related parties | HIGH | LLM analysis |

#### Category 4: Promoter Flags (6 flags)

| # | Flag Name | Severity | Detection Method |
|---|-----------|----------|------------------|
| 24 | Promoter pledge > 50% | CRITICAL | Percentage check |
| 25 | Promoter pledge increasing | HIGH | Trend analysis |
| 26 | Promoter shareholding declining | MEDIUM | Trend analysis |
| 27 | Frequent promoter changes | HIGH | Change count |
| 28 | Promoter transactions suspicious | HIGH | LLM analysis |
| 29 | Promoter compensation excessive | MEDIUM | Ratio to revenue |

#### Category 5: Corporate Governance (7 flags)

| # | Flag Name | Severity | Detection Method |
|---|-----------|----------|------------------|
| 30 | Independent directors < 50% | MEDIUM | Percentage check |
| 31 | CEO-Chairman same person | LOW | Text matching |
| 32 | Board meetings < 4 per year | MEDIUM | Count check |
| 33 | Audit committee composition weak | MEDIUM | Rule-based |
| 34 | Related party on board | MEDIUM | Entity matching |
| 35 | Frequent management changes | HIGH | Change count |
| 36 | Weak internal controls | HIGH | LLM analysis |

#### Category 6: Balance Sheet Flags (7 flags)

| # | Flag Name | Severity | Detection Method |
|---|-----------|----------|------------------|
| 37 | Debt/Equity > 2 | HIGH | Ratio calculation |
| 38 | Debt increasing rapidly | MEDIUM | CAGR check |
| 39 | Current ratio < 1 | HIGH | Ratio calculation |
| 40 | Receivables days > 90 | MEDIUM | DSO calculation |
| 41 | Inventory days increasing | MEDIUM | DIO trend |
| 42 | Intangible assets > 30% | MEDIUM | Percentage check |
| 43 | Contingent liabilities large | HIGH | Percentage of equity |

#### Category 7: Revenue Flags (5 flags)

| # | Flag Name | Severity | Detection Method |
|---|-----------|----------|------------------|
| 44 | Revenue recognition aggressive | HIGH | LLM analysis |
| 45 | Revenue growth but margin decline | MEDIUM | Trend comparison |
| 46 | One-time revenue spike | MEDIUM | Volatility check |
| 47 | Customer concentration high | MEDIUM | Percentage check |
| 48 | Revenue reversals | HIGH | Text matching |

#### Category 8: Textual Flags (6 flags) - **LLM-POWERED**

| # | Flag Name | Severity | Detection Method |
|---|-----------|----------|------------------|
| 49 | MD&A tone defensive | MEDIUM | Gemini sentiment |
| 50 | Increased jargon/complexity | MEDIUM | Gemini readability |
| 51 | Disclosure quality declining | MEDIUM | Gemini comparison |
| 52 | Risk factors expanding | MEDIUM | Section length trend |
| 53 | Contradictions in narrative | HIGH | Gemini consistency |
| 54 | Unusual audit language | HIGH | Gemini analysis |

### Flag Detection Workflow

```mermaid
graph TD
    A[Extracted Data] --> B{Category Router}
    B --> C[Auditor Flags]
    B --> D[Cash Flow Flags]
    B --> E[RPT Flags]
    B --> F[Promoter Flags]
    B --> G[Governance Flags]
    B --> H[Balance Sheet Flags]
    B --> I[Revenue Flags]
    B --> J[Textual Flags]
    
    C --> K[Flag Registry]
    D --> K
    E --> K
    F --> K
    G --> K
    H --> K
    I --> K
    J --> K
    
    K --> L[Risk Calculator]
    L --> M[Category Scores]
    L --> N[Overall Risk Score]
    M --> O[Analysis Result]
    N --> O
```

---

## Data Flow & Workflows

### 1. PDF Analysis Workflow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API
    participant C as Celery
    participant R as Redis
    participant G as Gemini
    participant D as Database
    participant S as R2 Storage

    U->>F: Upload PDF / Search Company
    F->>A: POST /api/v1/analysis/upload
    A->>S: Upload PDF to R2
    A->>R: Queue analysis job
    A->>F: Return job_id
    F->>A: WebSocket connect
    
    C->>R: Pick up job
    C->>A: Update: "Extracting text..."
    A->>F: WebSocket progress (30%)
    C->>S: Download PDF
    C->>C: PyMuPDF extraction
    
    C->>A: Update: "Detecting sections..."
    A->>F: WebSocket progress (50%)
    C->>G: Section detection prompt
    G->>C: Section page ranges
    
    C->>A: Update: "Extracting financials..."
    A->>F: WebSocket progress (60%)
    C->>G: Financial data extraction
    G->>C: Structured data
    
    C->>A: Update: "Checking red flags..."
    A->>F: WebSocket progress (70%)
    C->>C: Run 54 flag detectors
    
    C->>A: Update: "Calculating risk..."
    A->>F: WebSocket progress (90%)
    C->>C: Risk scoring algorithm
    
    C->>D: Save analysis result
    C->>A: Update: "Complete!"
    A->>F: WebSocket progress (100%)
    F->>A: GET /api/v1/reports/{id}
    A->>F: Return full results
    F->>U: Display risk score & flags
```

### 2. Watchlist Alert Workflow

```mermaid
sequenceDiagram
    participant S as Celery Beat
    participant C as Celery Worker
    participant D as Database
    participant E as Email Service
    participant P as Push Service
    participant U as User

    S->>C: Trigger daily check (8 AM UTC)
    C->>D: Fetch all watchlist items
    
    loop For each company
        C->>D: Get latest analysis
        C->>C: Compare with last_known_risk_score
        
        alt Score change >= 10 points
            C->>D: Create WatchlistAlert
            C->>D: Check user preferences
            
            alt Premium + real_time frequency
                C->>E: Send email alert
                E->>U: Email notification
                
                alt Push enabled
                    C->>P: Send push notification
                    P->>U: Browser notification
                end
            end
            
            C->>D: Update last_known_risk_score
        end
    end
    
    C->>D: Mark job complete
```

### 3. Portfolio Scanner Workflow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API
    participant S as Portfolio Service
    participant D as Database

    U->>F: Upload broker CSV
    F->>A: POST /api/v1/portfolio/upload
    A->>A: Check Premium subscription
    
    A->>S: Parse CSV
    S->>S: Detect broker format
    S->>S: Extract holdings
    
    loop For each symbol
        S->>D: Match to company
        S->>D: Get latest risk score
    end
    
    S->>S: Calculate portfolio metrics
    S->>D: Save portfolio & holdings
    A->>F: Return portfolio with risk heatmap
    F->>U: Display risk grid
```

### 4. Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API
    participant D as Database

    U->>F: Enter email/password
    F->>A: POST /api/v1/auth/login
    A->>D: Query user by email
    A->>A: Verify password hash
    A->>A: Generate JWT token
    A->>F: Return access + refresh tokens
    F->>F: Store in localStorage
    
    loop Protected requests
        F->>A: Request with Authorization header
        A->>A: Verify JWT signature
        A->>A: Check expiration
        A->>F: Return data
    end
    
    alt Token expired
        F->>A: POST /api/v1/auth/refresh
        A->>A: Verify refresh token
        A->>F: Return new access token
    end
```

---

## Background Jobs

### Celery Configuration ([celery_app.py](file:///d:/redflags/backend/app/celery_app.py))

```python
celery_app = Celery(
    "redflags",
    broker=settings.celery_broker_url,  # Redis
    backend=settings.celery_result_backend,  # Redis
    include=["app.tasks.analysis_tasks", "app.tasks.watchlist_tasks", "app.tasks.export_tasks"]
)
```

### Scheduled Tasks (Celery Beat)

| Task | Schedule | Purpose |
|------|----------|---------|
| `check_watchlist_alerts` | Daily 8 AM UTC | Check all watchlist items for score changes |
| `send_weekly_digest` | Monday 9 AM UTC | Send weekly summary to users with digest enabled |

### On-Demand Tasks

| Task | Trigger | Purpose |
|------|---------|---------|
| `analyze_report_task` | API request | Full PDF analysis pipeline |
| `send_real_time_alert_email` | Alert created | Immediate email for Premium users |
| `generate_user_data_export` | User request | Create ZIP with all user data |

### Task Queue Architecture

```
Redis (Broker)
    ├── analysis queue (high priority)
    ├── default queue (medium priority)
    └── low_priority queue (exports, digests)

Celery Workers
    ├── Worker 1: analysis tasks
    ├── Worker 2: analysis tasks
    └── Worker 3: alerts, exports
```

---

## External Integrations

### 1. Google Gemini API

**Purpose:** LLM-powered analysis

**Usage:**
- Section detection in PDFs
- Financial data extraction from tables
- Textual red flag detection (6 flags)
- Sentiment analysis of MD&A

**Configuration:**
```python
# app/llm/gemini_client.py
import google.generativeai as genai
genai.configure(api_key=settings.gemini_api_key)
model = genai.GenerativeModel('gemini-1.5-flash')
```

### 2. Brevo (Email Service)

**Purpose:** Transactional emails

**Email Types:**
- Watchlist alerts (real-time)
- Weekly digest
- Data export ready
- Password reset
- Welcome email

**Configuration:**
```python
# app/services/email_service.py
import sib_api_v3_sdk
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = settings.brevo_api_key
```

### 3. Cloudflare R2

**Purpose:** PDF storage

**Operations:**
- Upload annual reports
- Generate signed URLs for download
- Delete old reports

### 4. Supabase (PostgreSQL)

**Purpose:** Primary database

**Features:**
- Managed PostgreSQL 15
- Connection pooling
- Automatic backups
- Row-level security (optional)

### 5. Upstash (Redis)

**Purpose:** Cache and message broker

**Usage:**
- Celery broker
- Celery result backend
- Session storage (optional)
- Rate limiting (optional)

### 6. Web Push API

**Purpose:** Browser notifications

**Implementation:**
- VAPID authentication
- Service worker registration
- Subscription management
- Premium feature only

---

## Setup & Deployment

### Local Development Setup

#### Prerequisites

```bash
# Install required software
- Node.js 20.x LTS
- Python 3.11
- Docker Desktop
- PostgreSQL 15 (or use Supabase)
- Redis 7 (or use Upstash)
```

#### Backend Setup

```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
# Create .env file with:
DATABASE_URL=postgresql://user:pass@localhost:5432/redflags
REDIS_URL=redis://localhost:6379
GEMINI_API_KEY=your_key
BREVO_API_KEY=your_key
VAPID_PRIVATE_KEY=your_key
VAPID_PUBLIC_KEY=your_key
R2_ACCESS_KEY=your_key
R2_SECRET_KEY=your_key

# 5. Run database migrations
alembic upgrade head

# 6. Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 7. Start Celery worker (separate terminal)
celery -A app.celery_app worker --loglevel=info

# 8. Start Celery beat (separate terminal)
celery -A app.celery_app beat --loglevel=info
```

#### Frontend Setup

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Configure environment
# Create .env.local with:
NEXT_PUBLIC_API_URL=http://localhost:8000

# 4. Start development server
npm run dev

# Access at http://localhost:3000
```

### Production Deployment

#### Docker Compose

See [docker/docker-compose.yml](file:///d:/redflags/docker/) for full configuration.

```bash
# Build and start all services
docker-compose up -d

# Services:
# - postgres:5432
# - redis:6379
# - backend:8000
# - celery worker
# - celery beat
# - frontend:3000
```

#### Environment Variables (Production)

**Backend:**
```bash
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
GEMINI_API_KEY=...
BREVO_API_KEY=...
VAPID_PRIVATE_KEY=...
VAPID_PUBLIC_KEY=...
R2_ENDPOINT=...
R2_ACCESS_KEY=...
R2_SECRET_KEY=...
R2_BUCKET_NAME=redflags-pdfs
FRONTEND_URL=https://redflags.ai
```

**Frontend:**
```bash
NEXT_PUBLIC_API_URL=https://api.redflags.ai
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1

# View migration history
alembic history
```

---

## API Reference

### Authentication

#### POST /api/v1/auth/signup
Create new user account

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "subscription_tier": "free"
  }
}
```

#### POST /api/v1/auth/login
Login with email/password

#### POST /api/v1/auth/refresh
Refresh access token

#### GET /api/v1/auth/me
Get current user profile

### Companies

#### GET /api/v1/companies/search?q=reliance
Search companies by name or symbol

**Response:**
```json
{
  "results": [
    {
      "id": "uuid",
      "name": "Reliance Industries Ltd",
      "nse_symbol": "RELIANCE",
      "bse_code": "500325",
      "industry": "Oil & Gas",
      "sector": "Energy",
      "is_nifty_50": true
    }
  ]
}
```

### Analysis

#### POST /api/v1/analysis/upload
Upload PDF for analysis

**Request:** Multipart form-data
- `file`: PDF file (max 50MB)
- `company_name`: Optional company name

**Response:**
```json
{
  "job_id": "uuid",
  "status": "queued",
  "estimated_time_seconds": 45
}
```

#### GET /api/v1/analysis/job/{job_id}
Check analysis job status

**Response:**
```json
{
  "job_id": "uuid",
  "status": "processing",
  "progress": 65,
  "current_step": "Checking red flags...",
  "result_id": null
}
```

### Reports

#### GET /api/v1/reports/{report_id}
Get full analysis results

**Response:**
```json
{
  "id": "uuid",
  "company": {
    "name": "Reliance Industries Ltd",
    "nse_symbol": "RELIANCE"
  },
  "fiscal_year": "FY 2023-24",
  "risk_score": 67,
  "risk_level": "ELEVATED",
  "category_scores": {
    "auditor": 45,
    "cashflow": 72,
    "related_party": 58,
    "promoter": 35,
    "governance": 50,
    "balance_sheet": 60,
    "revenue": 40,
    "textual": 55
  },
  "flags_triggered_count": 12,
  "analyzed_at": "2026-02-07T10:30:00Z"
}
```

#### GET /api/v1/reports/{report_id}/flags
Get triggered red flags

**Response:**
```json
{
  "flags": [
    {
      "flag_number": 9,
      "flag_name": "Profit growing but CFO flat/declining",
      "category": "CASHFLOW",
      "severity": "HIGH",
      "confidence_score": 92.5,
      "evidence_text": "PAT growing at 18.5% CAGR but CFO flat at 3.2%",
      "page_references": [45, 47]
    }
  ]
}
```

### Portfolio

#### POST /api/v1/portfolio/upload
Upload broker CSV (Premium only)

**Request:** Multipart form-data
- `file`: CSV file
- `portfolio_name`: Portfolio name

**Response:**
```json
{
  "id": "uuid",
  "name": "My Zerodha Portfolio",
  "total_investment": 250000.00,
  "average_risk_score": 42.5,
  "high_risk_count": 3,
  "holdings": [
    {
      "symbol": "RELIANCE",
      "quantity": 10,
      "avg_price": 2500.00,
      "risk_score": 35,
      "risk_level": "LOW"
    }
  ]
}
```

### Watchlist

#### POST /api/v1/watchlist
Add company to watchlist

**Request:**
```json
{
  "company_id": "uuid",
  "alert_enabled": true
}
```

#### GET /api/v1/watchlist/alerts
Get watchlist alerts

**Query params:**
- `is_read`: Filter by read status
- `severity`: Filter by severity
- `limit`: Results per page

---

## Key Files Reference

### Backend Core Files

| File | Purpose | Lines |
|------|---------|-------|
| [main.py](file:///d:/redflags/backend/app/main.py) | FastAPI app entry point | 70 |
| [config.py](file:///d:/redflags/backend/app/config.py) | Environment configuration | ~100 |
| [database.py](file:///d:/redflags/backend/app/database.py) | Database connection | ~50 |
| [celery_app.py](file:///d:/redflags/backend/app/celery_app.py) | Celery configuration | 51 |

### Models

| File | Purpose | Lines |
|------|---------|-------|
| [user.py](file:///d:/redflags/backend/app/models/user.py) | User & subscription | 72 |
| [company.py](file:///d:/redflags/backend/app/models/company.py) | Company data | 60 |
| [analysis_result.py](file:///d:/redflags/backend/app/models/analysis_result.py) | Analysis results | ~100 |
| [red_flag.py](file:///d:/redflags/backend/app/models/red_flag.py) | Red flag records | ~80 |

### Red Flags

| File | Purpose | Flags |
|------|---------|-------|
| [base.py](file:///d:/redflags/backend/app/red_flags/base.py) | Base classes | - |
| [registry.py](file:///d:/redflags/backend/app/red_flags/registry.py) | Flag registry | - |
| [auditor_flags.py](file:///d:/redflags/backend/app/red_flags/auditor_flags.py) | Auditor checks | 8 |
| [cashflow_flags.py](file:///d:/redflags/backend/app/red_flags/cashflow_flags.py) | Cash flow checks | 8 |
| [related_party_flags.py](file:///d:/redflags/backend/app/red_flags/related_party_flags.py) | RPT checks | 7 |

### Frontend Core Files

| File | Purpose |
|------|---------|
| [layout.tsx](file:///d:/redflags/frontend/app/layout.tsx) | Root layout |
| [page.tsx](file:///d:/redflags/frontend/app/page.tsx) | Landing page |
| [(dashboard)/layout.tsx](file:///d:/redflags/frontend/app/(dashboard)/layout.tsx) | Dashboard layout |

---

## Appendix: Useful Commands

### Development

```bash
# Backend
uvicorn app.main:app --reload
celery -A app.celery_app worker --loglevel=info
celery -A app.celery_app beat --loglevel=info
alembic upgrade head

# Frontend
npm run dev
npm run build
npm run lint

# Database
psql -U postgres -d redflags
alembic current
alembic history
```

### Testing

```bash
# Backend tests
pytest backend/tests/
pytest backend/tests/test_red_flags.py -v

# Frontend tests
npm run test
npm run test:e2e
```

### Monitoring

```bash
# Celery monitoring with Flower
pip install flower
celery -A app.celery_app flower

# Access at http://localhost:5555
```

---

**End of Architecture Documentation**

For questions or updates, refer to:
- [QUICK_START.md](file:///d:/redflags/QUICK_START.md) - Setup guide
- [IMPLEMENTATION_SUMMARY.md](file:///d:/redflags/IMPLEMENTATION_SUMMARY.md) - Feature summary
- [docs/plan.md](file:///d:/redflags/docs/plan.md) - Master plan
