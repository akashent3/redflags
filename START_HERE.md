# 🚀 START HERE - Quick Setup

## ✅ Everything is Ready!

All bugs are fixed and the complete admin panel is built. Follow these steps to start testing.

---

## 1️⃣ Database Setup (5 minutes)

```sql
-- Connect to database
psql -U your_user -d redflags_db

-- Run migrations (if not done)
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(500);
\i backend/sql/create_fraud_cases_table.sql

-- Create admin user
UPDATE users SET is_admin = TRUE WHERE email = 'your@email.com';

-- Verify
SELECT email, is_admin FROM users WHERE is_admin = TRUE;
-- Should show your email with is_admin = t
```

---

## 2️⃣ Start Servers (2 minutes)

### Terminal 1 - Backend
```bash
cd D:\redflags\backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

### Terminal 2 - Frontend
```bash
cd D:\redflags\frontend
npm run dev
```

---

## 3️⃣ Test Pages (5 minutes)

### ✅ Watchlist
- URL: http://localhost:3000/watchlist
- Try adding "RELIANCE" or "TCS"
- Should work without errors

### ✅ Learn
- URL: http://localhost:3000/learn
- Should load (may be empty if no fraud cases)
- No dummy data errors

### ✅ Portfolio
- URL: http://localhost:3000/portfolio
- Upload CSV should work
- Real-time prices display

### ⭐ Admin Panel (NEW!)
- URL: http://localhost:3000/admin
- Should see dashboard with stats
- Try /admin/users, /admin/analyses, /admin/fraud-cases

---

## ⚠️ If Admin Panel Doesn't Show

### Check 1: Database
```sql
SELECT email, is_admin FROM users WHERE email = 'your@email.com';
```
Should show `is_admin = t`. If `f`, run:
```sql
UPDATE users SET is_admin = TRUE WHERE email = 'your@email.com';
```

### Check 2: Re-login
1. Logout from frontend
2. Login again (to get fresh token with is_admin flag)
3. Check browser console:
```javascript
console.log(JSON.parse(localStorage.getItem('user')))
// Should show: { ..., is_admin: true }
```

### Check 3: Backend Schema
Check if `backend/app/schemas/user.py` has:
```python
class UserResponse(BaseModel):
    # ...
    is_admin: bool  # ← Must have this field
```

If missing, add it and restart backend.

---

## 🎯 What to Expect

### Watchlist
- ✅ Page loads
- ✅ Can add companies by symbol
- ✅ Can delete companies
- ✅ Real-time prices display
- ✅ Risk scores show

### Learn Page
- ✅ Loads from database
- ✅ Empty state if no cases
- ✅ Search works
- ✅ No static data

### Admin Panel
- ✅ Sidebar shows "Admin" menu item (Shield icon)
- ✅ Dashboard shows statistics
- ✅ Can manage users
- ✅ Can manage analyses
- ✅ Can manage fraud cases

---

## 📚 Need Help?

- **Testing guide:** `FINAL_CHECKLIST.md`
- **Admin guide:** `ADMIN_PANEL_GUIDE.md`
- **Quick reference:** `README_FIXES.md`
- **Full summary:** `COMPLETE_SUMMARY.md`

---

## 🎉 You're All Set!

Everything is implemented and ready to test.

**Next:** Test the pages and enjoy your complete platform! 🚀
