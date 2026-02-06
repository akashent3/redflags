# Frontend Testing Guide - Phases 6 & 7

**Date**: February 6, 2026
**Frontend Status**: Phases 6 & 7 Complete (100%)
**Backend Status**: Running on http://localhost:8000
**Frontend Status**: Running on http://localhost:3000

---

## 🚀 Prerequisites

### 1. Start Backend Server
```bash
cd D:\redflags\backend
.\venv\Scripts\activate
uvicorn app.main:app --reload
```
**Expected**: Backend running at http://localhost:8000
**Verify**: Open http://localhost:8000/docs (Swagger UI should load)

### 2. Start Frontend Server
```bash
cd D:\redflags\frontend
npm run dev
```
**Expected**: Frontend running at http://localhost:3000
**Verify**: Terminal shows "Ready" message

---

## 📋 Testing Checklist

### ✅ **Test 1: Landing Page (Phase 7.1)**
**URL**: http://localhost:3000

**What to Check**:
- [ ] **Header**:
  - Logo and "RedFlag AI" text visible
  - "Sign in" button (ghost style)
  - "Get Started" button (primary style)
  - Header sticks to top on scroll

- [ ] **Hero Section**:
  - Badge: "AI-Powered Forensic Analysis"
  - Heading: "Your AI Forensic Accountant"
  - Subheading with value proposition
  - Two CTA buttons: "Start Free Trial" + "Sign In"
  - Small text: "Free tier: 3 reports per month • No credit card required"

- [ ] **Features Section** (3 cards):
  - **Card 1**: "54 Red Flag Detectors" with Shield icon (blue background)
  - **Card 2**: "Instant Analysis" with lightning icon (green background)
  - **Card 3**: "Risk Scoring" with bar chart icon (purple background)
  - Hover effects on cards (shadow increases)

- [ ] **How It Works Section** (3 steps):
  - Step 1: "Upload Report" with blue circle "1"
  - Step 2: "AI Analysis" with blue circle "2"
  - Step 3: "Get Insights" with blue circle "3"
  - Gray background section

- [ ] **Pricing Section** (3 tiers):
  - **Free**: ₹0/month, "Get Started" button (outline)
  - **Pro**: ₹499/month, "Start Pro Trial" button (primary), "Most Popular" badge
  - **Pro+**: ₹999/month, "Get Pro+" button (outline)
  - All checkmark icons visible
  - Border highlight on Pro tier (blue border)

- [ ] **Social Proof Section**:
  - Blue gradient background
  - Three stats: "54", "500+", "<60s"
  - White text on blue

- [ ] **CTA Section**:
  - Gradient background (blue → darker blue)
  - Heading: "Ready to Uncover Hidden Risks?"
  - Two buttons: "Start Free Trial" + "Sign In"

- [ ] **Footer**:
  - 4 columns: Brand, Product, Company, Legal
  - Logo and description in Brand column
  - All links present
  - Bottom bar with copyright + "Powered by Google Gemini AI"

**Navigation Tests**:
- [ ] Click "Sign in" → Redirects to `/login`
- [ ] Click "Get Started" → Redirects to `/signup`
- [ ] Click "Start Free Trial" → Redirects to `/signup`

**Responsive Tests**:
- [ ] Resize to mobile width (<640px) → Layout stacks vertically
- [ ] Resize to tablet (640-1024px) → 2-column grids
- [ ] Resize to desktop (>1024px) → 3-4 column grids

---

### ✅ **Test 2: Signup Page (Phase 6.3)**
**URL**: http://localhost:3000/signup

**What to Check**:
- [ ] **Layout**:
  - Centered card on gradient background
  - Logo at top
  - "Create your account" heading
  - Link to login page: "Already have an account? Sign in"

- [ ] **Form Fields**:
  - Full Name input
  - Email input
  - Password input
  - Confirm Password input
  - Terms checkbox (required)

- [ ] **Password Strength Indicator**:
  - Type password → strength meter appears
  - Colors: Red (Weak), Yellow (Fair), Blue (Good), Green (Strong)
  - Progress bar animates based on strength

- [ ] **Password Requirements Checklist**:
  - ✓ At least 8 characters (turns green when met)
  - ✓ Mix of uppercase and lowercase
  - ✓ At least one number
  - ✓ At least one special character

- [ ] **Validation**:
  - Submit empty form → Error messages appear
  - Type invalid email → "Please enter a valid email address"
  - Type short password → "Password must be at least 8 characters"
  - Passwords don't match → "Passwords do not match"
  - Check terms box → Checkbox required

- [ ] **Create Account**:
  - Fill valid data:
    - Full Name: Test User
    - Email: testuser@example.com
    - Password: Test123!@#
    - Confirm Password: Test123!@#
    - Check terms checkbox
  - Click "Create account"
  - Button shows loading spinner: "Creating account..."
  - On success → Auto-redirect to `/dashboard`

**Error Handling Tests**:
- [ ] Try existing email → "An account with this email already exists"
- [ ] Network error → "Unable to connect to server. Please try again."

---

### ✅ **Test 3: Login Page (Phase 6.3)**
**URL**: http://localhost:3000/login

**What to Check**:
- [ ] **Layout**:
  - Centered card on gradient background
  - "Welcome back" heading
  - Link to signup: "Don't have an account? Sign up"

- [ ] **Form Fields**:
  - Email input
  - Password input
  - "Remember me" checkbox
  - "Forgot password?" link

- [ ] **Social Login Placeholders**:
  - "Continue with Google" button
  - "Continue with GitHub" button
  - (These are placeholders for future implementation)

- [ ] **Login**:
  - Use credentials from signup:
    - Email: testuser@example.com
    - Password: Test123!@#
  - Click "Sign in"
  - Button shows loading spinner: "Signing in..."
  - On success → Redirect to `/dashboard`

**Error Handling Tests**:
- [ ] Wrong password → "Invalid email or password"
- [ ] Non-existent email → "Invalid email or password"
- [ ] Empty fields → Error messages appear

---

### ✅ **Test 4: Dashboard Page (Phase 7.2)**
**URL**: http://localhost:3000/dashboard
**Note**: Must be logged in to access

**What to Check**:
- [ ] **Header Component**:
  - Logo on left
  - Search bar in center
  - Notifications icon with badge (shows "3")
  - User avatar/icon on right

- [ ] **Sidebar Component**:
  - 6 navigation items:
    1. Dashboard (active - blue highlight)
    2. Analyze
    3. Portfolio
    4. Watchlist
    5. Learn
    6. Settings
  - Pro+ promotion card at bottom
  - Version info: "RedFlag AI v1.0.0"

- [ ] **Dashboard Header**:
  - Heading: "Dashboard"
  - Welcome message: "Welcome back, Test User!"

- [ ] **Stats Grid** (4 cards):
  - Total Reports: "0"
  - Avg Risk Score: "-"
  - Red Flags: "0"
  - Last Analysis: "-"
  - Each card has colored icon (blue, green, red, purple)

- [ ] **Welcome Card**:
  - Blue gradient background
  - Heading: "🎉 Welcome to RedFlag AI!"
  - Description text
  - Two buttons: "Analyze Report" + "Browse Companies"

- [ ] **Quick Actions** (3 cards):
  - Upload Report (Upload icon)
  - Search Company (Search icon)
  - Portfolio Scanner (BarChart3 icon)
  - Hover effect on cards

- [ ] **Recent Analyses Table**:
  - Shows 3 sample rows:
    1. Reliance Industries Ltd - Risk Score 42 (yellow badge) - 8 flags
    2. Tata Consultancy Services - Risk Score 28 (green badge) - 4 flags
    3. HDFC Bank Ltd - Risk Score 35 (green badge) - 6 flags
  - Columns: Company, Date, Risk Score, Red Flags, Status, Action
  - "View Report" button on each row
  - Hover effect on rows

- [ ] **Activity Timeline** (left widget):
  - 3 activities with icons:
    - Analyzed report - Reliance Industries Ltd - 2 hours ago
    - Added to watchlist - Infosys Ltd - 5 hours ago
    - Uploaded report - HDFC Bank Ltd - 1 day ago

- [ ] **Recommendations Widget** (right widget):
  - Blue gradient background
  - 3 recommendation cards:
    1. Complete your first analysis → "Get Started" button
    2. Learn about red flags → "Explore Cases" button
    3. Set up watchlist → "Add Companies" button

**Navigation Tests**:
- [ ] Click "Analyze Report" (welcome card) → Redirects to `/analyze`
- [ ] Click "Upload Report" (quick action) → Redirects to `/analyze`
- [ ] Click "Search Company" (quick action) → Redirects to `/analyze`
- [ ] Click "View Report" (table) → Redirects to `/report/1` (not built yet)
- [ ] Sidebar navigation works (click "Analyze") → Changes route

**Header Tests**:
- [ ] Click notifications icon → Dropdown opens with 3 sample notifications
- [ ] Click outside dropdown → Dropdown closes
- [ ] Click user avatar → User menu opens
- [ ] User menu shows: Name, email, Settings link, Logout button
- [ ] Click "Logout" → Redirects to `/login`, token cleared

**Mobile Tests**:
- [ ] Resize to mobile → Hamburger menu appears
- [ ] Click hamburger → Sidebar slides in from left
- [ ] Dark overlay appears behind sidebar
- [ ] Click overlay → Sidebar closes
- [ ] Click X button → Sidebar closes

---

### ✅ **Test 5: Analysis Page (Phase 7.3)**
**URL**: http://localhost:3000/analyze
**Note**: Must be logged in to access

**What to Check**:
- [ ] **Header**:
  - Heading: "Analyze Report"
  - Subheading: "Upload an annual report PDF or search for a NIFTY 500 company"

- [ ] **Tabs**:
  - Two tabs: "Upload PDF" + "Search Company"
  - Active tab has blue underline
  - Icons visible (Upload, Search)

#### **Upload PDF Tab Tests**:
- [ ] **Dropzone**:
  - Dashed border box
  - Upload icon in center
  - Text: "Drop your PDF here, or click to browse"
  - "Maximum file size: 50MB"
  - "Choose File" button (blue, primary style)

- [ ] **Drag & Drop**:
  - Drag a PDF file over dropzone → Border turns blue, background turns light blue
  - Drop PDF → File validation runs
  - Valid PDF → File info appears
  - Invalid file (e.g., .txt) → Error alert: "Please upload a PDF file"
  - Large file (>50MB) → Error alert: "File size must be less than 50MB"

- [ ] **File Selection via Button**:
  - Click "Choose File" → File picker opens
  - Select a PDF → File info appears

- [ ] **Selected File Display**:
  - File icon (blue background)
  - File name
  - File size in MB
  - X button to remove file

- [ ] **Upload Process**:
  - Click "Analyze Report" button
  - Button text changes to "Uploading & Analyzing..."
  - Loading spinner appears
  - Progress bar animates (0% → 100%)
  - Percentage shows: "10%", "20%", etc.
  - After 2 seconds → Redirects to `/report/1` (not built yet, will show 404)

- [ ] **Cancel**:
  - Click "Cancel" button → File removed, back to empty dropzone

- [ ] **Info Box**:
  - Blue background box appears after file selected
  - Text: "What happens next? We'll extract financial data..."

#### **Search Company Tab Tests**:
- [ ] **Search Bar**:
  - Search icon on left
  - Placeholder: "Search by company name or stock code..."
  - "Search" button on right

- [ ] **Empty State**:
  - Search icon in center
  - Text: "Search NIFTY 500 Companies"
  - "Enter a company name or stock code to get started"

- [ ] **Search Functionality**:
  - Type "Reliance" → Press Enter or click "Search"
  - Loading spinner appears in button
  - Results appear after 0.5 seconds
  - Shows matching companies (Reliance Industries Ltd)

- [ ] **Search Results**:
  - Company card shows:
    - Company name
    - Code: RELIANCE
    - Sector: Energy
    - "Analyze" button
  - Hover effect on card (border turns blue)

- [ ] **No Results**:
  - Type "xyz123" → Click "Search"
  - Shows: "No companies found"
  - "Try searching with a different name or stock code"

- [ ] **Popular Companies Section**:
  - Below search results
  - Heading: "Popular Companies"
  - 4 companies in 2x2 grid:
    1. Reliance Industries Ltd
    2. Tata Consultancy Services
    3. HDFC Bank Ltd
    4. Infosys Ltd
  - Click any company → Redirects to `/report/[id]`

**Search Test Cases**:
- [ ] Search "TCS" → Shows Tata Consultancy Services
- [ ] Search "INFY" → Shows Infosys Ltd
- [ ] Search "hdfc" (lowercase) → Shows HDFC Bank Ltd
- [ ] Search "banking" → Shows HDFC Bank, ICICI Bank

---

### ✅ **Test 6: Protected Routes (Phase 6.3)**

**What to Check**:
- [ ] **When Logged Out**:
  - Visit `/dashboard` → Auto-redirects to `/login`
  - Visit `/analyze` → Auto-redirects to `/login`
  - Visit `/portfolio` → Auto-redirects to `/login`

- [ ] **When Logged In**:
  - Visit `/` (landing page) → Auto-redirects to `/dashboard`
  - Visit `/login` → Auto-redirects to `/dashboard`
  - Visit `/signup` → Auto-redirects to `/dashboard`

---

### ✅ **Test 7: Authentication Flow (End-to-End)**

**Full User Journey**:
1. [ ] Visit http://localhost:3000 → Sees landing page
2. [ ] Click "Get Started" → Redirects to `/signup`
3. [ ] Fill signup form → Creates account
4. [ ] Auto-login → Redirects to `/dashboard`
5. [ ] See welcome message with name
6. [ ] Click "Analyze Report" → Redirects to `/analyze`
7. [ ] Upload PDF or search company
8. [ ] Click notifications icon → Dropdown opens
9. [ ] Click user avatar → User menu opens
10. [ ] Click "Logout" → Redirects to `/login`
11. [ ] Login again → Redirects to `/dashboard`
12. [ ] Refresh page → Still logged in (token persists)

---

### ✅ **Test 8: Responsive Design**

**Mobile (< 640px)**:
- [ ] Landing page: Single column, stacked sections
- [ ] Dashboard: Sidebar hidden, hamburger menu visible
- [ ] Stats grid: 1 column
- [ ] Recent analyses table: Horizontal scroll
- [ ] Buttons: Full width

**Tablet (640-1024px)**:
- [ ] Landing page: 2-column grids
- [ ] Dashboard: Sidebar visible, no hamburger
- [ ] Stats grid: 2 columns
- [ ] Quick actions: 2 columns

**Desktop (> 1024px)**:
- [ ] Landing page: 3-4 column grids
- [ ] Dashboard: Sidebar always visible
- [ ] Stats grid: 4 columns
- [ ] Quick actions: 3 columns

---

### ✅ **Test 9: Error Handling**

**Network Errors**:
- [ ] Stop backend server
- [ ] Try to login → "Unable to connect to server"
- [ ] Try to signup → "Unable to connect to server"

**Validation Errors**:
- [ ] Signup with existing email → "An account with this email already exists"
- [ ] Login with wrong password → "Invalid email or password"
- [ ] Upload non-PDF file → "Please upload a PDF file"
- [ ] Upload large file (>50MB) → "File size must be less than 50MB"

**Loading States**:
- [ ] All buttons show spinners during API calls
- [ ] Upload shows progress bar
- [ ] Search shows loading state

---

### ✅ **Test 10: Visual Polish**

**Animations & Transitions**:
- [ ] Sidebar slide-in animation (300ms)
- [ ] Dropdown fade-in animations
- [ ] Progress bar animation (smooth 0-100%)
- [ ] Button hover effects (color change)
- [ ] Card hover effects (shadow increase)

**Color Consistency**:
- [ ] Primary blue: #2563eb (buttons, links, borders)
- [ ] Success green: Green-600 (checkmarks, low risk)
- [ ] Warning yellow: Yellow-600 (medium risk)
- [ ] Danger red: Red-600 (high risk)

**Typography**:
- [ ] Headings: Bold, gray-900
- [ ] Body text: Regular, gray-700
- [ ] Muted text: gray-500/600
- [ ] Consistent font sizes

---

## 🐛 Known Issues to Check

1. **Backend Connection**:
   - [ ] Ensure backend is running before testing
   - [ ] Check CORS is enabled in backend
   - [ ] Verify API base URL is correct (`http://localhost:8000`)

2. **Browser Console**:
   - [ ] Open DevTools (F12)
   - [ ] Check Console tab for errors
   - [ ] No red errors should appear during normal usage

3. **Network Tab**:
   - [ ] Open DevTools → Network tab
   - [ ] Login → Check POST `/api/v1/auth/login` returns 200
   - [ ] Signup → Check POST `/api/v1/auth/signup` returns 201
   - [ ] All requests should have `Authorization: Bearer <token>` header

---

## ✅ Success Criteria

### All Tests Pass If:
- [x] Landing page loads with all sections
- [x] Signup creates new account
- [x] Login authenticates user
- [x] Dashboard shows user info and stats
- [x] Analysis page allows upload and search
- [x] Protected routes redirect when not logged in
- [x] Logout clears token and redirects
- [x] Mobile menu works (hamburger → sidebar)
- [x] Dropdowns close on outside click
- [x] File upload validates correctly
- [x] Search filters companies
- [x] No console errors
- [x] Responsive design works

---

## 📊 Testing Results Template

```markdown
## Testing Results - February 6, 2026

**Tester**: [Your Name]
**Browser**: [Chrome/Firefox/Edge]
**Screen Size**: [1920x1080 / Mobile / Tablet]

### Passed Tests:
- [ ] Landing Page
- [ ] Signup Page
- [ ] Login Page
- [ ] Dashboard Page
- [ ] Analysis Page
- [ ] Protected Routes
- [ ] Authentication Flow
- [ ] Responsive Design
- [ ] Error Handling
- [ ] Visual Polish

### Issues Found:
1. [Issue description]
2. [Issue description]

### Overall Status:
- Total Tests: 10
- Passed: X
- Failed: Y
- Pass Rate: X%
```

---

## 🚀 Quick Start Testing Script

```bash
# 1. Start Backend
cd D:\redflags\backend
.\venv\Scripts\activate
uvicorn app.main:app --reload

# 2. Open new terminal, Start Frontend
cd D:\redflags\frontend
npm run dev

# 3. Open Browser
# Visit http://localhost:3000

# 4. Test Signup
# Email: test@example.com
# Password: Test123!@#

# 5. Test Login
# Use same credentials

# 6. Explore Dashboard
# Click all buttons and links

# 7. Test Analysis Page
# Try upload and search tabs

# 8. Test Logout
# Click user menu → Logout
```

---

## 📝 Notes

- All sample data is hardcoded for Phase 7 testing
- Real API integration will be added in Phase 8
- Results page (`/report/[id]`) will be built in Phase 8
- Portfolio, Watchlist, Learn pages will be built in Phases 10-11

---

**Testing Duration**: ~30-45 minutes for complete testing
**Priority**: Test signup → login → dashboard → analyze first
**Report Issues**: Note any bugs or unexpected behavior

Good luck with testing! 🎉
