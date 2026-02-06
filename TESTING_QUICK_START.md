# 🚀 Quick Start Testing Guide

**Status**: Ready to test Phases 6 & 7 (Frontend Foundation + Core Pages)

---

## ⚡ Start Servers

### 1. Start Backend (Terminal 1)
```bash
cd D:\redflags\backend
.\venv\Scripts\activate
uvicorn app.main:app --reload
```
✅ **Expected**: Server running at http://localhost:8000

### 2. Start Frontend (Terminal 2)
```bash
cd D:\redflags\frontend
npm run dev
```
✅ **Expected**: Server running at http://localhost:3000

---

## 🧪 5-Minute Quick Test

### Step 1: Landing Page (30 seconds)
- Open: http://localhost:3000
- ✅ Check: Hero section, features (3 cards), pricing (3 tiers), footer
- ✅ Click: "Get Started" button → Should go to `/signup`

### Step 2: Signup (1 minute)
- On signup page
- ✅ Fill form:
  ```
  Full Name: Test User
  Email: test123@example.com
  Password: Test123!@#
  Confirm Password: Test123!@#
  ☑ I agree to terms
  ```
- ✅ Watch: Password strength meter (should show "Strong" in green)
- ✅ Click: "Create account"
- ✅ Expected: Auto-redirect to `/dashboard`

### Step 3: Dashboard (1 minute)
- ✅ Check: "Welcome back, Test User!" message
- ✅ Check: 4 stats cards (Total Reports, Risk Score, Red Flags, Last Analysis)
- ✅ Check: Recent Analyses table (3 sample rows)
- ✅ Check: Activity Timeline (left widget)
- ✅ Check: Recommendations (right widget)
- ✅ Click: Hamburger menu icon → Sidebar slides in (mobile test)

### Step 4: Analysis Page (1.5 minutes)
- ✅ Click: "Analyze Report" button from dashboard
- ✅ Expected: Redirects to `/analyze`

#### Upload Tab:
- ✅ Drag a PDF file onto dropzone → Border turns blue
- ✅ Drop file → File name and size appear
- ✅ Click: "Analyze Report" → Progress bar animates (0-100%)
- ✅ Expected: Redirects to `/report/1` after 2 seconds

#### Search Tab:
- ✅ Click: "Search Company" tab
- ✅ Type: "Reliance" → Click "Search"
- ✅ Expected: Shows Reliance Industries Ltd card
- ✅ Check: Popular Companies section shows 4 companies

### Step 5: Logout & Login (1 minute)
- ✅ Click: User avatar (top right) → Dropdown opens
- ✅ Click: "Logout" → Redirects to `/login`
- ✅ Login with:
  ```
  Email: test123@example.com
  Password: Test123!@#
  ```
- ✅ Expected: Redirects to `/dashboard`

---

## ✅ What Should Work

### Pages:
- ✅ Landing page with hero, features, pricing, footer
- ✅ Signup with password strength meter
- ✅ Login with validation
- ✅ Dashboard with stats, table, timeline, recommendations
- ✅ Analysis page with upload + search tabs

### Features:
- ✅ Authentication (signup, login, logout)
- ✅ Protected routes (dashboard, analyze require login)
- ✅ JWT token persistence (refresh page stays logged in)
- ✅ Form validation (email format, password strength)
- ✅ File upload validation (PDF only, 50MB max)
- ✅ Company search filtering
- ✅ Responsive design (mobile menu)
- ✅ Dropdowns (notifications, user menu)
- ✅ Loading states (spinners, progress bars)
- ✅ Error messages (user-friendly)

### Components:
- ✅ Header with logo, search, notifications, user menu
- ✅ Sidebar with 6 navigation items
- ✅ Footer with 4 columns
- ✅ Stats cards with icons
- ✅ Recent analyses table
- ✅ Activity timeline
- ✅ Recommendations widget
- ✅ Drag & drop upload
- ✅ Company search results

---

## 🎯 Key Testing Points

### 1. Responsive Design
- **Desktop**: Sidebar always visible, 3-4 column grids
- **Mobile**: Hamburger menu, sidebar slides in, 1 column

### 2. Authentication
- **Protected Routes**: `/dashboard` and `/analyze` redirect to `/login` when not logged in
- **Auto-Redirect**: Landing page redirects to `/dashboard` when logged in
- **Token Persistence**: Refresh page while logged in → stays logged in

### 3. Validation
- **Email**: Must be valid format (has @ and domain)
- **Password**: Min 8 chars, uppercase, lowercase, number, special char
- **File**: PDF only, max 50MB
- **Required Fields**: All fields must be filled

### 4. Visual Feedback
- **Loading**: Spinners on buttons during API calls
- **Progress**: Animated progress bar (0-100%)
- **Hover**: Cards and buttons have hover effects
- **Active**: Current page highlighted in sidebar (blue)
- **Errors**: Red alerts with icons

---

## 🐛 Common Issues & Fixes

### Issue: "Unable to connect to server"
**Fix**: Start backend server
```bash
cd D:\redflags\backend
.\venv\Scripts\activate
uvicorn app.main:app --reload
```

### Issue: Login shows "Invalid credentials"
**Fix**: Make sure you created account first via signup

### Issue: Dashboard shows loading forever
**Fix**:
1. Check backend is running: http://localhost:8000/docs
2. Check browser console for errors (F12)
3. Verify token exists in localStorage (F12 → Application → Local Storage)

### Issue: File upload doesn't work
**Fix**: Make sure file is PDF format and < 50MB

### Issue: Sidebar doesn't open on mobile
**Fix**: Click hamburger menu icon (three lines) in header

---

## 📊 Test Results Template

```markdown
## My Test Results

**Date**: February 6, 2026
**Browser**: [Chrome/Firefox]
**Status**: [PASS/FAIL]

### Passed:
- [ ] Landing page loads
- [ ] Signup creates account
- [ ] Login works
- [ ] Dashboard shows data
- [ ] Analysis page works
- [ ] Upload validates files
- [ ] Search filters companies
- [ ] Mobile menu works
- [ ] Logout works

### Issues:
1. [Description]

### Overall: ✅ PASS / ❌ FAIL
```

---

## 🎨 What You'll See

### Landing Page:
- Modern hero section with badge
- 3 feature cards with colored icons
- 3-step "How It Works" with numbered circles
- 3 pricing tiers (Free, Pro, Pro+)
- Blue social proof section
- Gradient CTA section
- 4-column footer

### Dashboard:
- Header with logo, search, notifications, user menu
- Left sidebar with 6 navigation items
- Stats grid (4 cards)
- Recent analyses table (3 rows)
- Activity timeline (3 items)
- Recommendations widget (3 cards)

### Analysis Page:
- Two tabs: Upload PDF / Search Company
- Drag & drop dropzone
- File validation with error messages
- Upload progress bar
- Company search with results
- Popular companies section

---

## 📞 Need Help?

### Check Logs:
- **Frontend**: Check terminal running `npm run dev`
- **Backend**: Check terminal running `uvicorn`
- **Browser**: Press F12 → Console tab

### Verify Setup:
- Backend docs: http://localhost:8000/docs
- Frontend: http://localhost:3000
- Both servers must be running

### Test Credentials:
```
Email: test123@example.com
Password: Test123!@#
```

---

## 🎉 Success!

If all tests pass:
- ✅ Phase 6 (Frontend Foundation) - 100% working
- ✅ Phase 7 (Core Pages) - 100% working
- ✅ Ready to proceed to Phase 8 (Results Visualization)

**Total Frontend Progress**: 50% complete (7/15 phases)
**Next Phase**: Phase 8 - Results Visualization (Risk Gauge, Spider Chart, Red Flags)

---

**Testing Time**: ~5 minutes (quick test) or ~30 minutes (comprehensive)
**Priority**: Test signup → login → dashboard → analyze first

Good luck! 🚀
