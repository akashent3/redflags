# Session Changes — RedFlag AI

## Overview
This document covers all fixes, features, and improvements implemented in this development session.

---

## 1. Bug Fixes

### 1.1 R2 Storage — Wrong Object Key Extraction
**Problem:** PDF downloads from Cloudflare R2 were failing with `NoSuchKey` error. The URL stored in the database is `stockforensic.com/reports/uuid/...` (no `https://` prefix), so splitting by `/` 3 times was cutting into the actual file path and producing a truncated key.

**Root Cause:**
```python
# Before — wrong for URLs without https:// prefix
object_key = pdf_url.split("/", 3)[-1]
# "stockforensic.com/reports/uuid/file.pdf".split("/", 3)[-1]
# → "2024-2025/annual_report.pdf"  ❌ Missing "reports/uuid/" prefix
```

**Fix — strip the base URL directly:**
```python
base = settings.r2_public_url.rstrip("/")
object_key = pdf_url[len(base):].lstrip("/")
# → "reports/uuid/2024-2025/annual_report.pdf"  ✅
```

**Files Changed:**
- `backend/app/tasks/analysis_tasks.py` — 2 places (lines ~88 and ~298)
- `backend/app/api/v1/reports.py` — delete endpoint

---

### 1.2 Watchlist Auto-Analysis — Celery Task Not Starting
**Problem:** When adding a company to the watchlist, the Celery analysis task was never dispatched to the worker queue. The task showed as "Pending" forever.

**Root Cause:**
```python
# Before — WRONG: wraps .delay() inside BackgroundTasks
background_tasks.add_task(
    analyze_company_by_symbol_task.delay,
    symbol=symbol
)
# FastAPI's BackgroundTasks just calls .delay as a plain function,
# returns the AsyncResult object and discards it — task never reaches Celery
```

**Fix:**
```python
# After — call .delay() directly
task = analyze_company_by_symbol_task.delay(symbol, str(current_user.id))
logger.info(f"✓ Celery task dispatched: {task.id} for symbol {symbol}")
```

**Also fixed:** `user_id` was missing from the task call (required for `UserAnalysis` tracking).

**File Changed:** `backend/app/api/v1/watchlist.py`

---

### 1.3 Pattern Match — `AnalysisResult` Has No `company_id`
**Problem:** `POST /fraud-cases/pattern-match/{analysis_id}` was throwing `'AnalysisResult' object has no attribute 'company_id'`.

**Root Cause:** `AnalysisResult` model has no direct `company_id` column — the company is reached via `AnnualReport`. Also `analysis.red_flags` relationship is commented out in the model.

**Fix:**
```python
# Get company via AnnualReport (not directly from AnalysisResult)
annual_report = db.query(AnnualReport).filter(AnnualReport.id == analysis.report_id).first()
company = db.query(Company).filter(Company.id == annual_report.company_id).first()

# Query RedFlag table directly (red_flags relationship is commented out)
triggered_flags = {
    flag.flag_number
    for flag in db.query(RedFlag).filter(
        RedFlag.analysis_id == analysis.id,
        RedFlag.is_triggered == True
    ).all()
}
```

**File Changed:** `backend/app/api/v1/fraud_cases.py`

---

### 1.4 Portfolio Page Showing Blank/Upload Screen After Upload
**Problem:** After uploading a CSV, the page returned to the upload screen instead of showing holdings.

**Root Cause:** Frontend called `api.get<Portfolio[]>('/portfolio/')` but backend returns `{ portfolios: Portfolio[], total: number }`. So `response.data` was an object, `response.data.length` was `undefined`, and `currentPortfolio` was never set.

**Fix:**
```typescript
const response = await api.get<{ portfolios: Portfolio[]; total: number }>('/portfolio/');
const portfolioList = response.data.portfolios || [];
setPortfolios(portfolioList);
if (portfolioList.length > 0) {
  setCurrentPortfolio(portfolioList[0]);
}
```

**File Changed:** `frontend/app/(dashboard)/portfolio/page.tsx`

---

### 1.5 Pattern Match Route Conflict — `/my-companies` Intercepted by `/{analysis_id}`
**Problem:** `GET /analysis/my-companies` returned a 500 error because FastAPI matched it against the `GET /{analysis_id}` wildcard route (defined earlier in the file), treating `"my-companies"` as an analysis UUID.

**Fix:** Moved `GET /my-companies` to be defined **before** `GET /{analysis_id}` in `analysis.py`. Removed the duplicate definition at the bottom of the file.

**File Changed:** `backend/app/api/v1/analysis.py`

---

### 1.6 Admin Getting 403 on Portfolio/Watchlist Premium Endpoints
**Problem:** Admin users were getting `Access Forbidden` on portfolio upload and push notification endpoints.

**Fix:** Added `not current_user.is_admin` bypass to all premium checks:
```python
if not current_user.is_admin and current_user.subscription_tier != 'premium':
    raise HTTPException(status_code=403, ...)
```

**Files Changed:**
- `backend/app/api/v1/portfolio.py`
- `backend/app/api/v1/watchlist.py` (push notification preferences + subscription endpoint)

---

### 1.7 Portfolio Duplicate on Re-Upload
**Problem:** Every CSV upload created a new portfolio, accumulating duplicates. Re-uploading the same file would show 2, 3, 4 portfolios.

**Fix:** Before creating a new portfolio, delete all existing portfolios for the user:
```python
existing_portfolios = db.query(Portfolio).filter(Portfolio.user_id == current_user.id).all()
for old_portfolio in existing_portfolios:
    db.delete(old_portfolio)
if existing_portfolios:
    db.flush()
```

Cascade delete on `Portfolio → Holding` handles holdings automatically.

**File Changed:** `backend/app/api/v1/portfolio.py`

---

### 1.8 `AnalysisResult` Has No `red_flags` — Portfolio Service
**Problem:** `'AnalysisResult' object has no attribute 'red_flags'` in portfolio service when building risk data.

**Root Cause:** `red_flags` relationship is commented out in `analysis_result.py`. Flag counts are stored as columns: `flags_triggered_count`, etc.

**Fix:**
```python
# Before (broken):
flags_count = sum(1 for f in latest_analysis.red_flags if f.is_triggered)

# After (correct):
'flags_count': latest_analysis.flags_triggered_count,  # stored column
```

**File Changed:** `backend/app/services/portfolio_service.py`

---

## 2. New Features

### 2.1 Auto-Analysis on Watchlist Add
When a user adds a company to their watchlist that has no existing analysis, the system automatically dispatches a Celery background task to run the full analysis pipeline (fetch from NSE → upload to R2 → AI analysis → store results).

- **Trigger condition:** `if not latest_analysis` — only if truly no analysis exists
- **Task:** `analyze_company_by_symbol_task.delay(symbol, user_id)`
- **Frontend:** Shows spinning "Analyzing..." badge instead of "Pending"; polls `GET /watchlist/` every 10 seconds until all scores appear, then stops polling automatically

**Files Changed:**
- `backend/app/api/v1/watchlist.py`
- `frontend/app/(dashboard)/watchlist/page.tsx`

---

### 2.2 Auto-Analysis on Portfolio Upload
Same auto-trigger logic applied to portfolio CSV upload. After creating holdings, any company with no existing risk score automatically gets an analysis task dispatched.

- **Trigger condition:** `if risk_info.get('risk_score') is None` — only if no score exists
- **Frontend:** Shows spinning "Analyzing..." in risk column; polls `GET /portfolio/` every 10 seconds until all holdings have scores

**Files Changed:**
- `backend/app/api/v1/portfolio.py`
- `frontend/app/(dashboard)/portfolio/page.tsx`

---

### 2.3 View Report Button on Portfolio Page
Each holding in the portfolio now has a "View Report" button (📄 icon) that navigates to `/report/{latest_analysis_id}`, same as the watchlist page.

**Implementation:**
- **Model:** Added `latest_analysis_id = Column(String(36), nullable=True)` to `Holding` model
- **Schema:** Added `latest_analysis_id: Optional[str]` to `HoldingResponse`
- **Service:** `get_risk_scores()` now returns `latest_analysis_id` in risk dict; added `get_latest_analysis_id_for_company()` for live fallback lookup when stored value is NULL
- **API:** Both GET `/portfolio/` and GET `/portfolio/{id}` endpoints populate `latest_analysis_id`, with live DB fallback for old holdings
- **Frontend:** Added "Report" column with FileText icon button; `—` shown if no analysis exists

**Migration required:**
```sql
ALTER TABLE holdings ADD COLUMN IF NOT EXISTS latest_analysis_id VARCHAR(36);
```

**Files Changed:**
- `backend/app/models/portfolio.py`
- `backend/app/schemas/portfolio.py`
- `backend/app/services/portfolio_service.py`
- `backend/app/api/v1/portfolio.py`
- `frontend/app/(dashboard)/portfolio/page.tsx`
- `frontend/lib/types/portfolio.ts`

---

### 2.4 Pattern Match Feature on Learn Page
The "Check Your Stock for Fraud Patterns" section on the Learn page now fully works.

**Flow:**
1. User opens the pattern match section
2. Autocomplete search shows companies from user's analyses, watchlist, and portfolio
3. User selects a company
4. Clicking "Analyze Patterns" calls `GET /companies/{id}/latest-analysis` to get the analysis ID, then `POST /fraud-cases/pattern-match/{analysis_id}`
5. Results displayed inline — risk level badge, message, flag count, and top matching fraud cases with similarity percentages

**Backend:** `POST /fraud-cases/pattern-match/{analysis_id}` uses Jaccard similarity algorithm:
- `< 30%` → LOW risk
- `30–50%` → MEDIUM risk
- `50–70%` → HIGH risk
- `> 70%` → CRITICAL risk

**Files Changed:**
- `backend/app/api/v1/fraud_cases.py` (fixed bugs)
- `frontend/app/(dashboard)/learn/page.tsx`

---

### 2.5 Autocomplete on Learn Page — User's Companies
The pattern match search bar now auto-loads companies from the user's history.

**New endpoint:** `GET /analysis/my-companies`
- Fetches companies from 3 sources for the current user:
  1. **Analyses:** `UserAnalysis` → `AnalysisResult` → `AnnualReport` → `Company`
  2. **Watchlist:** `WatchlistItem` → `Company`
  3. **Portfolio:** `Portfolio` → `Holding` → `Company`
- Deduplicates by company ID, sorts alphabetically
- Returns `{ companies: [{id, name, nse_symbol}], total: N }`

**Note below search bar:** *"Only companies whose reports have been generated — via Analyze, Watchlist, or Portfolio — are shown in suggestions."*

**File Changed:** `backend/app/api/v1/analysis.py`

---

### 2.6 CSV File Upload Button Fix
**Problem:** Clicking "Choose CSV File" button on portfolio page did nothing (no file picker opened).

**Root Cause:** `<Button>` inside `<label>` swallows the click event in browsers — the file input is never triggered.

**Fix:** Use `useRef<HTMLInputElement>` and call `fileInputRef.current?.click()` directly from the button's `onClick`.

**File Changed:** `frontend/app/(dashboard)/portfolio/page.tsx`

---

### 2.7 Premium User Check — Real Auth Instead of Hardcoded
Portfolio page was hardcoded to `useState(true)` for `isPremiumUser`. Fixed to read actual user data from `localStorage`:

```typescript
const isPremiumUser = currentUser?.is_admin || currentUser?.subscription_tier === 'premium';
```

**File Changed:** `frontend/app/(dashboard)/portfolio/page.tsx`

---

## 3. Data Model Changes

### 3.1 `holdings` Table — New Column
```sql
ALTER TABLE holdings ADD COLUMN latest_analysis_id VARCHAR(36);
```

### 3.2 `User` Interface — Frontend
Added `is_admin: boolean` to the `User` TypeScript interface in `frontend/lib/types/api.ts`.

### 3.3 `Holding` Interface — Frontend
Updated `frontend/lib/types/portfolio.ts`:
- Added: `holding_id`, `price_change`, `price_change_percent`, `latest_analysis_id`
- Changed `risk_level` from union type to `string` (backend uses `ELEVATED` and others)
- Made `average_risk_score` optional on `Portfolio`
- Added `description?: string` to `Portfolio`

---

## 4. Files Changed — Complete List

### Backend
| File | Changes |
|------|---------|
| `app/api/v1/watchlist.py` | Auto-trigger analysis; fixed BackgroundTasks→Celery.delay(); removed BackgroundTasks import |
| `app/api/v1/portfolio.py` | Auto-trigger analysis on upload; portfolio replacement; admin bypass; `latest_analysis_id` in holdings |
| `app/api/v1/analysis.py` | Added `GET /my-companies` endpoint (before `/{analysis_id}` to avoid route conflict) |
| `app/api/v1/fraud_cases.py` | Fixed `company_id` lookup via AnnualReport; fixed `red_flags` → direct RedFlag query |
| `app/api/v1/reports.py` | Fixed R2 object key extraction in delete endpoint |
| `app/tasks/analysis_tasks.py` | Fixed R2 object key extraction in 2 places |
| `app/models/portfolio.py` | Added `latest_analysis_id` column to `Holding` |
| `app/schemas/portfolio.py` | Added `latest_analysis_id` to `HoldingResponse` |
| `app/services/portfolio_service.py` | Added `get_latest_analysis_id_for_company()`; `get_risk_scores()` now returns `latest_analysis_id`; fixed ordering by `analyzed_at` |

### Frontend
| File | Changes |
|------|---------|
| `app/(dashboard)/portfolio/page.tsx` | Fixed response shape; CSV button ref fix; real auth check; polling; View Report button; Analyzing spinner |
| `app/(dashboard)/watchlist/page.tsx` | Polling every 10s for pending analysis; "Analyzing..." spinner |
| `app/(dashboard)/learn/page.tsx` | Pattern match autocomplete; `handlePatternMatch`; results display; note text |
| `lib/types/portfolio.ts` | Updated `Holding` and `Portfolio` interfaces |
| `lib/types/api.ts` | Added `is_admin: boolean` to `User` interface |

---

## 5. Architecture Notes

### Auto-Analysis Flow
```
User adds company (watchlist/portfolio)
    ↓
Backend checks: does latest_analysis exist?
    ↓ NO
analyze_company_by_symbol_task.delay(symbol, user_id)
    ↓
Celery worker picks up task
    ↓
Downloads annual report from NSE → uploads to R2
    ↓
Runs AI analysis → stores AnalysisResult + RedFlag rows
    ↓
Creates UserAnalysis tracking record
    ↓
Frontend polls GET /watchlist/ or GET /portfolio/ every 10s
    ↓
Score appears → polling stops automatically
```

### Pattern Match Flow
```
User types company name in Learn page search
    ↓
GET /analysis/my-companies → autocomplete from user's history
    ↓
User selects company, clicks "Analyze Patterns"
    ↓
GET /companies/{id}/latest-analysis → get analysis_id
    ↓
POST /fraud-cases/pattern-match/{analysis_id}
    ↓
Backend: get triggered RedFlags → Jaccard similarity vs fraud cases
    ↓
Returns top 5 matches with similarity % and matching flags
    ↓
Displayed inline with risk level badge
```

### R2 Object Key Extraction (Correct Pattern)
```python
# The URL stored in DB: "stockforensic.com/reports/uuid/file.pdf"
# R2_PUBLIC_URL setting: "stockforensic.com"

base = settings.r2_public_url.rstrip("/")
object_key = pdf_url[len(base):].lstrip("/")
# Result: "reports/uuid/file.pdf"  ✅
```
