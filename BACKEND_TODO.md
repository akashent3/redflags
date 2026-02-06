# Backend Implementation TODO

**Date**: February 6, 2026
**Status**: Frontend Complete (57%), Backend Partially Complete

---

## Overview

This document tracks all backend implementation tasks needed to integrate with the completed frontend features from Phases 9-11.

---

## ✅ COMPLETED Backend Features

### 1. Core Infrastructure
- [x] FastAPI application setup
- [x] PostgreSQL database with SQLAlchemy
- [x] Authentication (JWT, signup, login)
- [x] Company search API
- [x] PDF extraction pipeline
- [x] Celery for background jobs
- [x] 54 red flag detectors
- [x] Risk scoring engine
- [x] Analysis API endpoints

### 2. Recently Added (Phase 10-11)
- [x] Watchlist database models (`models/watchlist.py`)
- [x] Portfolio database models (`models/portfolio.py`)
- [x] Watchlist schemas (`schemas/watchlist.py`)
- [x] Portfolio schemas (`schemas/portfolio.py`)
- [x] Watchlist API endpoints (`api/v1/watchlist.py`)
- [x] User model relationships (watchlist, portfolios, notification prefs)

---

## ⏳ PENDING Backend Implementation

### Priority 1: Critical Path (Week 11-12)

#### 1. Portfolio API with CSV Parsing
**File**: `backend/app/api/v1/portfolio.py`
**Status**: ❌ Not Started

**Endpoints to Create**:
```python
@router.post("/portfolio/upload")
async def upload_portfolio_csv(
    file: UploadFile,
    portfolio_name: str = "My Portfolio",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Parse CSV, create portfolio, match companies, fetch risk scores.

    Steps:
    1. Validate file format (.csv only, max 10MB)
    2. Detect broker format (Zerodha/Groww/Upstox/Generic)
    3. Parse CSV with pandas
    4. Map columns: Symbol, Quantity, Avg Price
    5. Calculate investment_value = quantity * avg_price
    6. Match symbols to company_id via database lookup
    7. Fetch latest risk_score for each company
    8. Create Portfolio and Holding records
    9. Calculate aggregate metrics (total_investment, average_risk_score, high_risk_count)
    10. Return CSVUploadResponse with matched/unmatched counts
    """

@router.get("/portfolio")
async def get_portfolios(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get user's portfolios."""

@router.get("/portfolio/{portfolio_id}")
async def get_portfolio(
    portfolio_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get portfolio details with holdings."""

@router.delete("/portfolio/{portfolio_id}")
async def delete_portfolio(
    portfolio_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete portfolio."""
```

**CSV Parsing Logic**:
```python
# backend/app/services/portfolio_service.py
import pandas as pd
from typing import List, Tuple

BROKER_FORMATS = {
    'zerodha': {'symbol': 'symbol', 'quantity': 'quantity', 'avg_price': 'average_price'},
    'groww': {'symbol': 'stock_name', 'quantity': 'qty', 'avg_price': 'avg_cost'},
    'upstox': {'symbol': 'symbol', 'quantity': 'quantity', 'avg_price': 'buy_avg'},
    'generic': {'symbol': 'Symbol', 'quantity': 'Quantity', 'avg_price': 'Avg Price'},
}

def detect_broker_format(df: pd.DataFrame) -> str:
    """Detect CSV format by column names."""
    columns = set(df.columns)
    for broker, mapping in BROKER_FORMATS.items():
        if all(col in columns for col in mapping.values()):
            return broker
    return 'generic'

def parse_portfolio_csv(file_content: bytes) -> List[HoldingCreate]:
    """Parse CSV and return standardized holdings."""
    df = pd.read_csv(io.BytesIO(file_content))
    broker = detect_broker_format(df)
    mapping = BROKER_FORMATS[broker]

    holdings = []
    for _, row in df.iterrows():
        holdings.append(HoldingCreate(
            symbol=row[mapping['symbol']].strip().upper(),
            quantity=int(row[mapping['quantity']]),
            avg_price=float(row[mapping['avg_price']]),
        ))

    return holdings

def match_symbols_to_companies(db: Session, symbols: List[str]) -> Tuple[dict, List[str]]:
    """Match symbols to company IDs. Returns (matched_dict, unmatched_list)."""
    matched = {}
    unmatched = []

    for symbol in symbols:
        company = db.query(Company).filter(
            (Company.nse_symbol == symbol) | (Company.bse_code == symbol)
        ).first()

        if company:
            matched[symbol] = company
        else:
            unmatched.append(symbol)

    return matched, unmatched
```

**Dependencies**: `pandas`, `openpyxl` (for Excel support)

---

#### 2. Celery Watchlist Alert Tasks
**File**: `backend/app/tasks/watchlist_tasks.py`
**Status**: ❌ Not Started

**Tasks to Create**:
```python
from celery import shared_task
from app.database import SessionLocal
from app.models.watchlist import WatchlistItem, WatchlistAlert
from app.models.analysis_result import AnalysisResult

@shared_task
def check_watchlist_alerts():
    """
    Periodic task (runs daily) to check all watchlist items for alerts.

    Logic:
    1. Fetch all active watchlist items
    2. For each item:
       a. Get latest analysis
       b. Compare current risk_score with last_known_risk_score
       c. If change >= 10 points, create SCORE_CHANGE alert
       d. Update last_known_risk_score and last_checked_at
    3. Generate email/push notifications based on user preferences
    """
    db = SessionLocal()
    try:
        items = db.query(WatchlistItem).filter(
            WatchlistItem.alert_enabled == True
        ).all()

        for item in items:
            # Get latest analysis
            latest = db.query(AnalysisResult).filter(
                AnalysisResult.company_id == item.company_id
            ).order_by(AnalysisResult.created_at.desc()).first()

            if not latest:
                continue

            current_score = latest.overall_risk_score
            previous_score = item.last_known_risk_score

            # Check for significant change (>=10 points)
            if previous_score and abs(current_score - previous_score) >= 10:
                # Determine severity
                severity = "CRITICAL" if current_score >= 60 else "WARNING" if current_score >= 40 else "INFO"

                # Create alert
                alert = WatchlistAlert(
                    watchlist_item_id=item.id,
                    alert_type="SCORE_CHANGE",
                    severity=severity,
                    message=f"Risk score changed from {previous_score} to {current_score} ({current_score - previous_score:+d} points)",
                    previous_risk_score=previous_score,
                    current_risk_score=current_score,
                    score_change=current_score - previous_score,
                )
                db.add(alert)

                # Update watchlist item
                item.last_known_risk_score = current_score
                item.last_checked_at = datetime.utcnow()

        db.commit()
    finally:
        db.close()


@shared_task
def send_weekly_digest():
    """
    Weekly task to send digest emails to users with weekly_digest_enabled.

    Logic:
    1. Fetch users with weekly_digest_enabled=True
    2. For each user:
       a. Fetch unread alerts from past 7 days
       b. Group by company
       c. Generate HTML email template
       d. Send via email service
    """


@shared_task
def send_real_time_alert(user_id: str, alert_id: str):
    """
    Send immediate email/push for critical alerts (Premium users only).

    Logic:
    1. Check user subscription_tier == 'premium'
    2. Fetch alert details
    3. Send email via service
    4. Send push notification if enabled
    """
```

**Celery Beat Schedule** (add to `celery_app.py`):
```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    'check-watchlist-alerts-daily': {
        'task': 'app.tasks.watchlist_tasks.check_watchlist_alerts',
        'schedule': crontab(hour=8, minute=0),  # 8 AM daily
    },
    'send-weekly-digest': {
        'task': 'app.tasks.watchlist_tasks.send_weekly_digest',
        'schedule': crontab(day_of_week=1, hour=9, minute=0),  # Monday 9 AM
    },
}
```

---

#### 3. Database Migrations
**Files**: `backend/alembic/versions/XXXX_add_watchlist_portfolio.py`
**Status**: ❌ Not Created

**Migration Steps**:
```bash
# Create migration
cd backend
alembic revision --autogenerate -m "Add watchlist and portfolio models"

# Apply migration
alembic upgrade head
```

**Tables to Create**:
- `watchlist_items` (with foreign keys to users, companies)
- `watchlist_alerts` (with foreign key to watchlist_items)
- `notification_preferences` (with foreign key to users)
- `portfolios` (with foreign key to users)
- `holdings` (with foreign keys to portfolios, companies)

**Enums to Create**:
- `alert_type_enum`: SCORE_CHANGE, NEW_FLAGS, NEW_REPORT
- `alert_severity_enum`: INFO, WARNING, CRITICAL
- `alert_frequency_enum`: real_time, daily, weekly, none

---

### Priority 2: User Features (Week 12)

#### 4. Profile Management API
**File**: `backend/app/api/v1/users.py` (extend existing)
**Status**: ⚠️ Partially Complete (needs additional endpoints)

**Endpoints to Add**:
```python
@router.patch("/users/profile")
async def update_profile(
    data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update user name and email."""

@router.post("/users/password")
async def change_password(
    data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Change user password with old password verification."""

@router.post("/users/profile-picture")
async def upload_profile_picture(
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Upload profile picture to Cloudflare R2.
    1. Validate image format (JPEG, PNG, GIF)
    2. Resize to 256x256px
    3. Upload to R2 bucket
    4. Save URL to user.profile_picture_url
    """

@router.get("/users/export-data")
async def export_user_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Generate ZIP with all user data:
    - Analysis reports (JSON)
    - Watchlist (CSV)
    - Portfolio holdings (CSV)
    - Notification preferences (JSON)

    Background task to generate ZIP, email download link.
    """

@router.delete("/analyses/delete-all")
async def delete_all_analyses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Permanently delete user's analysis history."""

@router.delete("/users/delete-account")
async def delete_account(
    confirmation: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Permanently delete user account.
    1. Verify confirmation string matches email
    2. Delete all related data (analyses, watchlist, portfolios, alerts)
    3. Revoke JWT tokens
    4. Send confirmation email
    """
```

**Schemas**:
```python
# backend/app/schemas/users.py
class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)
```

---

#### 5. Fraud Cases API
**File**: `backend/app/api/v1/fraud_cases.py`
**Status**: ❌ Not Started

**Endpoints to Create**:
```python
@router.get("/fraud-cases")
async def get_fraud_cases(
    sector: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
):
    """
    Get fraud cases with filtering.

    For MVP: Return static data from fraud_cases.json
    For production: Store in database and query dynamically
    """

@router.get("/fraud-cases/{case_id}")
async def get_fraud_case_detail(case_id: str):
    """Get detailed fraud case information."""

@router.post("/fraud-cases/pattern-match")
async def match_fraud_patterns(company_id: UUID):
    """
    Analyze company for fraud pattern matches.

    Algorithm:
    1. Fetch company's latest analysis
    2. Get list of triggered red flags
    3. For each fraud pattern:
       a. Count matching flags
       b. Calculate similarity = (matching / pattern_total) * 100
    4. Return patterns with similarity >= 50%
    5. Generate risk assessment and recommendation
    """
```

**Data Storage Options**:
1. **MVP**: JSON file (`backend/app/data/fraud_cases.json`) - Simple, fast
2. **Production**: Database table - Searchable, scalable

**Pattern Matching Logic**:
```python
# backend/app/services/fraud_pattern_service.py
def match_patterns(triggered_flags: List[int], patterns: List[FraudPattern]) -> List[PatternMatch]:
    """Match company flags against fraud patterns."""
    matches = []

    for pattern in patterns:
        # Count matching flags
        matching = set(triggered_flags) & set(pattern.common_flags)
        similarity = (len(matching) / len(pattern.common_flags)) * 100

        if similarity >= 50:  # Threshold for match
            matches.append(PatternMatch(
                pattern_name=pattern.pattern_name,
                confidence=similarity,
                matching_flags=list(matching),
            ))

    # Determine overall risk
    if any(m.confidence >= 80 for m in matches):
        risk = "CRITICAL"
    elif any(m.confidence >= 60 for m in matches):
        risk = "HIGH"
    elif matches:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return matches, risk
```

---

### Priority 3: Payment & Subscription (Week 13)

#### 6. Razorpay Subscription Integration
**File**: `backend/app/api/v1/subscriptions.py`
**Status**: ❌ Not Started

**Endpoints to Create**:
```python
@router.post("/subscriptions/create-order")
async def create_razorpay_order(
    plan: str,  # 'pro' or 'premium'
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create Razorpay order for subscription.

    Steps:
    1. Determine amount based on plan (₹999 or ₹1999)
    2. Create Razorpay order via API
    3. Store order_id in database
    4. Return order details for frontend Razorpay checkout
    """

@router.post("/subscriptions/verify-payment")
async def verify_razorpay_payment(
    payment_data: RazorpayPaymentData,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Verify Razorpay payment signature and upgrade subscription.

    Steps:
    1. Verify signature: HMAC SHA256(order_id + "|" + razorpay_payment_id, secret)
    2. Verify payment status via Razorpay API
    3. Upgrade user.subscription_tier
    4. Update user.reports_limit
    5. Send confirmation email
    6. Return success response
    """

@router.post("/subscriptions/downgrade")
async def schedule_downgrade(
    plan: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Schedule downgrade at end of billing cycle.

    Logic:
    1. Set scheduled_downgrade_tier and scheduled_downgrade_date
    2. On downgrade date (Celery task), update subscription_tier
    """

@router.get("/subscriptions/invoices")
async def get_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get user's payment history and invoices."""
```

**Razorpay Setup**:
```python
# backend/app/services/razorpay_service.py
import razorpay

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

def create_order(amount: int, currency: str = "INR") -> dict:
    """Create Razorpay order."""
    return client.order.create({
        "amount": amount * 100,  # Convert to paise
        "currency": currency,
        "payment_capture": 1,  # Auto-capture
    })

def verify_signature(order_id: str, payment_id: str, signature: str) -> bool:
    """Verify payment signature."""
    import hmac
    import hashlib

    message = f"{order_id}|{payment_id}".encode()
    generated_signature = hmac.new(
        RAZORPAY_KEY_SECRET.encode(),
        message,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(generated_signature, signature)
```

---

### Priority 4: Email & Notifications (Week 13-14)

#### 7. Email Service
**File**: `backend/app/services/email_service.py`
**Status**: ❌ Not Started

**Setup Options**:
1. **SendGrid** (Recommended for production)
2. **AWS SES** (Cost-effective for high volume)
3. **SMTP** (Simple for MVP)

**Email Templates to Create**:
```python
# backend/app/templates/email/

# 1. watchlist_alert_email.html
# 2. weekly_digest_email.html
# 3. subscription_confirmation_email.html
# 4. password_reset_email.html
# 5. account_deletion_confirmation_email.html
```

**Email Service Functions**:
```python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_watchlist_alert(user_email: str, alert: WatchlistAlert):
    """Send immediate alert email."""

def send_weekly_digest(user_email: str, alerts: List[WatchlistAlert]):
    """Send weekly digest email."""

def send_subscription_confirmation(user_email: str, plan: str):
    """Send subscription upgrade confirmation."""
```

---

#### 8. Push Notifications
**File**: `backend/app/services/push_service.py`
**Status**: ❌ Not Started

**Web Push Setup**:
```python
from pywebpush import webpush

def send_push_notification(subscription_info: dict, message: dict):
    """
    Send web push notification.

    Steps:
    1. Parse subscription_info (endpoint, keys)
    2. Build notification payload
    3. Send via Web Push Protocol
    4. Handle errors (expired subscription, etc.)
    """
    webpush(
        subscription_info=subscription_info,
        data=json.dumps(message),
        vapid_private_key=VAPID_PRIVATE_KEY,
        vapid_claims={"sub": "mailto:support@redflag-ai.com"}
    )
```

**VAPID Keys Generation**:
```bash
pip install py-vapid
vapid --gen
# Save public/private keys to .env
```

---

## Testing Checklist

### API Testing (Postman/Insomnia)

#### Watchlist
- [ ] GET /api/v1/watchlist - Get user's watchlist
- [ ] POST /api/v1/watchlist - Add company to watchlist
- [ ] DELETE /api/v1/watchlist/{id} - Remove from watchlist
- [ ] GET /api/v1/watchlist/alerts - Get alerts
- [ ] PATCH /api/v1/watchlist/alerts/{id} - Mark alert as read
- [ ] GET /api/v1/watchlist/preferences - Get notification preferences
- [ ] PATCH /api/v1/watchlist/preferences - Update notification preferences

#### Portfolio
- [ ] POST /api/v1/portfolio/upload - Upload CSV file
- [ ] GET /api/v1/portfolio - Get user's portfolios
- [ ] GET /api/v1/portfolio/{id} - Get portfolio details
- [ ] DELETE /api/v1/portfolio/{id} - Delete portfolio

#### Fraud Cases
- [ ] GET /api/v1/fraud-cases - List fraud cases
- [ ] GET /api/v1/fraud-cases/{id} - Get case details
- [ ] POST /api/v1/fraud-cases/pattern-match - Match patterns

#### Profile
- [ ] PATCH /api/v1/users/profile - Update profile
- [ ] POST /api/v1/users/password - Change password
- [ ] POST /api/v1/users/profile-picture - Upload picture
- [ ] GET /api/v1/users/export-data - Export data
- [ ] DELETE /api/v1/analyses/delete-all - Delete history
- [ ] DELETE /api/v1/users/delete-account - Delete account

#### Subscriptions
- [ ] POST /api/v1/subscriptions/create-order - Create Razorpay order
- [ ] POST /api/v1/subscriptions/verify-payment - Verify payment
- [ ] POST /api/v1/subscriptions/downgrade - Schedule downgrade
- [ ] GET /api/v1/subscriptions/invoices - Get invoices

### Background Tasks Testing
- [ ] Watchlist alert generation (daily)
- [ ] Weekly digest email (Monday 9 AM)
- [ ] Real-time alert email (Premium users)
- [ ] Push notifications (Premium users)
- [ ] Data export ZIP generation
- [ ] Subscription downgrade scheduler

---

## Dependencies to Add

### Python Packages
```txt
# backend/requirements.txt additions
pandas>=2.0.0                  # CSV parsing
openpyxl>=3.1.0               # Excel support
razorpay>=1.4.0               # Payment processing
sendgrid>=6.10.0              # Email service
pywebpush>=1.14.0             # Push notifications
py-vapid>=1.9.0               # VAPID keys for push
Pillow>=10.0.0                # Image processing for profile pictures
```

### Environment Variables
```bash
# backend/.env additions
# Razorpay
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=xxxxx

# SendGrid
SENDGRID_API_KEY=SG.xxxxx
FROM_EMAIL=noreply@redflag-ai.com

# Web Push
VAPID_PRIVATE_KEY=xxxxx
VAPID_PUBLIC_KEY=xxxxx
VAPID_CLAIM_EMAIL=support@redflag-ai.com
```

---

## Timeline Estimate

| Priority | Task | Estimated Time | Depends On |
|----------|------|---------------|------------|
| P1 | Portfolio API + CSV Parser | 2-3 days | Database migrations |
| P1 | Database Migrations | 0.5 day | - |
| P1 | Celery Watchlist Tasks | 1-2 days | Database migrations |
| P2 | Profile Management API | 1 day | - |
| P2 | Fraud Cases API | 1 day | - |
| P3 | Razorpay Integration | 2 days | - |
| P4 | Email Service + Templates | 2 days | - |
| P4 | Push Notifications | 1 day | Email service |

**Total Estimated Time**: 10-12 days (2 weeks)

---

## Notes

### CSV Parsing Edge Cases
- Handle missing columns
- Handle different date formats
- Handle multiple sheets in Excel
- Handle UTF-8 encoding issues
- Validate numeric values (quantity, price)
- Trim whitespace from symbols

### Watchlist Alert Logic
- Threshold of 10 points is configurable
- Alert frequency respects user preferences
- Deduplicate alerts (don't spam for same change)
- Clean up old alerts (>90 days)

### Security Considerations
- Validate file uploads (size, type, content)
- Rate limit CSV uploads (max 5 per hour per user)
- Sanitize user input (SQL injection, XSS)
- Verify Razorpay signatures server-side
- Encrypt sensitive data (push subscription keys)

### Performance Optimizations
- Cache risk scores for portfolio lookups
- Batch company symbol matching
- Index watchlist queries (user_id, company_id)
- Use database transactions for data integrity

---

**Last Updated**: February 6, 2026
**Next Review**: After Priority 1 completion

---

## Quick Start Commands

```bash
# Run database migrations
cd backend
alembic upgrade head

# Start Celery worker
celery -A app.celery_app worker --loglevel=info

# Start Celery beat (scheduler)
celery -A app.celery_app beat --loglevel=info

# Run FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

*Documentation generated for backend integration tracking*
