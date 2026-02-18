# Critical Fixes Needed for RedFlag AI

**Date:** 2026-02-16
**Status:** Issues found during testing

---

## 🐛 **Critical Issues Found**

### 1. Watchlist Page - Type Mismatch ✅ FIXED
**Issue:** Frontend expects array `WatchlistItem[]` but backend returns `{items: [], alerts: []}`

**Root Cause:** Backend returns `WatchlistResponse` schema with nested structure

**Fix Applied:**
- Updated frontend interface to match backend schema
- Changed field names: `added_at` → `added_date`, `change` → `price_change`, `change_percent` → `price_change_percent`
- Extract `items` from response: `response.data.items`

**Status:** ✅ **FIXED**

---

### 2. Watchlist Add Function - Endpoint Mismatch ❌ **NEEDS FIX**
**Issue:** Frontend calls `POST /watchlist/add` with `{symbol}` but backend expects `POST /watchlist/` with `{company_id}`

**Root Cause:** No symbol-based add endpoint exists

**Solution Options:**

**Option A (Recommended): Create symbol-based backend endpoint**
```python
# backend/app/api/v1/watchlist.py

@router.post(
    "/add-by-symbol",
    response_model=WatchlistItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add company to watchlist by symbol",
)
async def add_to_watchlist_by_symbol(
    symbol: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Add company to watchlist by symbol (searches company first)."""
    # Search for company by symbol
    company = db.query(Company).filter(
        (Company.nse_symbol == symbol.upper()) |
        (Company.display_code == symbol.upper())
    ).first()

    if not company:
        raise HTTPException(404, f"Company with symbol {symbol} not found")

    # Check if already in watchlist
    existing = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == current_user.id,
        WatchlistItem.company_id == company.id
    ).first()

    if existing:
        raise HTTPException(409, "Company already in watchlist")

    # Create watchlist item
    # ... (rest of logic similar to existing POST / endpoint)
```

**Option B: Update frontend to search then add**
```typescript
// frontend/app/(dashboard)/watchlist/page.tsx

const handleAddSymbol = async () => {
  if (!newSymbol.trim()) return;

  try {
    setAddingSymbol(true);
    setError(null);

    // 1. Search for company
    const searchResponse = await api.get(`/companies/search?query=${newSymbol.toUpperCase()}&limit=1`);

    if (searchResponse.data.total === 0) {
      throw new Error(`Company with symbol ${newSymbol} not found`);
    }

    const company = searchResponse.data.results[0];

    // 2. Add to watchlist using company_id
    await api.post('/watchlist/', {
      company_id: company.id,
      alert_enabled: true,
    });

    setNewSymbol('');
    await fetchWatchlist();
  } catch (err: any) {
    console.error('Failed to add symbol:', err);
    setError(err.response?.data?.detail || err.message || 'Failed to add symbol to watchlist');
  } finally {
    setAddingSymbol(false);
  }
};
```

**Recommendation:** Use Option B (frontend fix) as it requires no backend changes and uses existing endpoints.

**Status:** ❌ **NEEDS FIX**

---

### 3. Admin Panel - Missing Frontend UI ❌ **NEEDS IMPLEMENTATION**
**Issue:** Admin backend is complete, but no admin UI exists in frontend

**What's Missing:**
- No `/admin` route in Next.js
- No admin navigation in sidebar (for admin users)
- No admin pages (users, analyses, fraud cases, stats)

**Backend Ready:**
- ✅ `GET /api/v1/admin/stats` - System statistics
- ✅ `GET /api/v1/admin/users` - List users
- ✅ `PATCH /api/v1/admin/users/{user_id}/subscription` - Update subscription
- ✅ `DELETE /api/v1/admin/users/{user_id}` - Delete user
- ✅ `GET /api/v1/admin/analyses` - List analyses
- ✅ `DELETE /api/v1/admin/analyses/{analysis_id}` - Delete analysis
- ✅ `DELETE /api/v1/admin/fraud-cases/{case_id}` - Delete fraud case

**Implementation Needed:**

**Step 1: Add admin check to useAuth hook**
```typescript
// frontend/lib/hooks/useAuth.ts
export interface User {
  id: string;
  email: string;
  full_name: string;
  is_admin: boolean; // ADD THIS
  subscription_tier: string;
}
```

**Step 2: Add admin navigation to Sidebar**
```typescript
// frontend/components/layout/Sidebar.tsx
import { Shield } from 'lucide-react';

// Inside the component, get user from context
const user = useUser(); // You'll need to create this context

const navItems = [
  // ... existing items
  ...(user?.is_admin ? [{
    name: 'Admin',
    href: '/admin',
    icon: Shield,
    description: 'System administration',
  }] : []),
];
```

**Step 3: Create admin pages**
```
frontend/app/(dashboard)/admin/
├── page.tsx              # Dashboard with stats
├── users/
│   └── page.tsx          # User management
├── analyses/
│   └── page.tsx          # Analysis management
└── fraud-cases/
    └── page.tsx          # Fraud case management
```

**Status:** ❌ **NEEDS IMPLEMENTATION** (Backend ready, frontend missing)

---

### 4. Learn Page (Fraud Cases) - Using Static JSON ❌ **NEEDS FIX**
**Issue:** Learn page still uses static JSON data instead of fetching from database

**Current Code:**
```typescript
import { FRAUD_CASES, FRAUD_PATTERNS } from '@/lib/data/fraudCases';
```

**Backend Endpoint Ready:**
- ✅ `GET /api/v1/fraud-cases/` - List all fraud cases from database

**Fix Needed:**
```typescript
// frontend/app/(dashboard)/learn/page.tsx

interface FraudCase {
  case_id: string;
  company_name: string;
  year: number;
  sector: string;
  fraud_type: string;
  stock_decline_percent: number;
  market_cap_lost_cr: number;
  red_flags_detected: any[];
  timeline?: any[];
  lessons_learned?: any[];
  pdf_url?: string;
}

export default function LearnPage() {
  const [fraudCases, setFraudCases] = useState<FraudCase[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFraudCases();
  }, []);

  const fetchFraudCases = async () => {
    try {
      setLoading(true);
      const response = await api.get<FraudCase[]>('/fraud-cases/');
      setFraudCases(response.data);
    } catch (error) {
      console.error('Failed to fetch fraud cases:', error);
    } finally {
      setLoading(false);
    }
  };

  // Rest of the component uses fraudCases instead of FRAUD_CASES
}
```

**Status:** ❌ **NEEDS FIX**

---

### 5. Watchlist Delete - Endpoint Mismatch ⚠️ **CHECK NEEDED**
**Issue:** Frontend calls `DELETE /watchlist/{symbol}` but backend expects `DELETE /watchlist/{watchlist_id}`

**Frontend Code:**
```typescript
const handleRemoveSymbol = async (symbol: string) => {
  await api.delete(`/watchlist/${symbol}`);
};
```

**Backend Endpoint:**
```python
@router.delete("/{watchlist_id}", ...)
async def remove_from_watchlist(watchlist_id: UUID, ...):
```

**Fix:**
```typescript
const handleRemoveSymbol = async (watchlistId: string) => {
  if (!confirm(`Remove this company from watchlist?`)) return;

  try {
    await api.delete(`/watchlist/${watchlistId}`);
    await fetchWatchlist();
  } catch (err: any) {
    console.error('Failed to remove from watchlist:', err);
    setError(err.response?.data?.detail || 'Failed to remove');
  }
};

// Update button to pass watchlist_id instead of symbol
<Button onClick={() => handleRemoveSymbol(item.watchlist_id)}>
  <Trash2 className="h-4 w-4" />
</Button>
```

**Status:** ⚠️ **CHECK NEEDED**

---

## 📋 **Fix Priority**

### High Priority (Breaks functionality)
1. ✅ **Watchlist response type mismatch** - FIXED
2. ❌ **Watchlist add function** - Backend endpoint needed OR frontend search-then-add
3. ⚠️ **Watchlist delete function** - Use watchlist_id instead of symbol

### Medium Priority (Missing features)
4. ❌ **Learn page fraud cases** - Connect to API instead of static JSON
5. ❌ **Admin panel frontend** - Create UI for admin features

### Low Priority (Nice to have)
- Admin panel is fully functional on backend, just needs frontend UI
- Could be built incrementally

---

## 🔧 **Recommended Quick Fixes**

### Fix 1: Watchlist Add (Frontend only - no backend changes)
Update `frontend/app/(dashboard)/watchlist/page.tsx`:

```typescript
const handleAddSymbol = async () => {
  if (!newSymbol.trim()) return;

  try {
    setAddingSymbol(true);
    setError(null);

    // Search for company first
    const searchResponse = await api.get(`/companies/search?query=${newSymbol.toUpperCase()}&limit=1`);

    if (searchResponse.data.total === 0) {
      setError(`Company with symbol "${newSymbol}" not found. Try searching from the Analyze page first.`);
      return;
    }

    const company = searchResponse.data.results[0];

    // Add to watchlist using company_id
    await api.post('/watchlist/', {
      company_id: company.id,
      alert_enabled: true,
    });

    setNewSymbol('');
    await fetchWatchlist();
  } catch (err: any) {
    console.error('Failed to add symbol:', err);
    setError(err.response?.data?.detail || 'Failed to add symbol to watchlist');
  } finally {
    setAddingSymbol(false);
  }
};
```

### Fix 2: Watchlist Delete (Frontend only)
Update delete handler to use `watchlist_id`:

```typescript
const handleRemoveSymbol = async (watchlistId: string) => {
  // Confirmation already handled in onClick
  try {
    await api.delete(`/watchlist/${watchlistId}`);
    await fetchWatchlist();
  } catch (err: any) {
    console.error('Failed to remove from watchlist:', err);
    setError(err.response?.data?.detail || 'Failed to remove');
  }
};

// In JSX:
<Button onClick={() => handleRemoveSymbol(item.watchlist_id)}>
  <Trash2 className="h-4 w-4" />
</Button>
```

### Fix 3: Learn Page (Frontend only)
Replace static JSON with API call - see detailed code above in Issue #4.

---

## ✅ **Testing After Fixes**

1. **Watchlist**
   - [ ] Page loads without errors
   - [ ] Real-time prices display
   - [ ] Add company by symbol works
   - [ ] Delete company works
   - [ ] Risk scores display correctly

2. **Learn Page**
   - [ ] Fraud cases load from database
   - [ ] Empty state shows if no cases
   - [ ] Case details display correctly

3. **Admin Panel** (After implementation)
   - [ ] Admin users see admin nav item
   - [ ] Non-admin users don't see it
   - [ ] Stats page loads
   - [ ] User management works
   - [ ] Analysis management works

---

**Next Steps:**
1. Apply watchlist fixes (add & delete)
2. Update learn page to use API
3. (Optional) Build admin panel frontend

All fixes can be done frontend-only without any backend changes!
