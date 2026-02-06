# RedFlag AI - Frontend

## Phase 6: Frontend Foundation

AI-powered forensic accounting scanner for analyzing corporate annual reports.

---

## Tech Stack

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui (Radix UI primitives)
- **Data Fetching**: TanStack React Query (React Query)
- **HTTP Client**: Axios
- **Charts**: Recharts
- **Advanced Graphics**: D3.js
- **Icons**: Lucide React
- **State Management**: React Context + React Query

---

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Landing page
│   └── globals.css        # Global styles
├── components/            # React components
│   └── ui/               # shadcn/ui components
├── lib/                   # Utilities and hooks
│   ├── api/              # API client
│   │   └── client.ts     # Axios instance
│   ├── hooks/            # Custom React hooks
│   │   └── useAuth.ts    # Authentication hook
│   ├── types/            # TypeScript types
│   │   └── api.ts        # API types
│   └── utils.ts          # Utility functions
├── public/               # Static assets
├── .env.local           # Environment variables
├── next.config.ts       # Next.js configuration
├── tailwind.config.ts   # Tailwind configuration
├── tsconfig.json        # TypeScript configuration
└── package.json         # Dependencies
```

---

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Backend server running on http://localhost:8000

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

---

## Available Scripts

- `npm run dev` - Start development server (http://localhost:3000)
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

---

## API Integration

### API Client (`lib/api/client.ts`)

The API client is pre-configured with:
- Base URL from environment variables
- JWT token authentication (auto-added to requests)
- Error handling and response interceptors
- 401 handling (auto-logout and redirect)

### Usage Example

```typescript
import { api } from '@/lib/api/client';

// GET request
const response = await api.get('/companies/search?q=reliance');

// POST request
const result = await api.post('/auth/login', { username, password });

// File upload
const upload = await api.upload('/reports/upload', file, {
  company_name: 'TCS',
  fiscal_year: 2023
});
```

---

## Authentication

### useAuth Hook

```typescript
import { useAuth } from '@/lib/hooks/useAuth';

function Component() {
  const { user, isAuthenticated, login, logout } = useAuth();

  const handleLogin = async () => {
    await login('user@example.com', 'password');
  };

  return (
    <div>
      {isAuthenticated ? (
        <p>Welcome {user?.full_name}</p>
      ) : (
        <button onClick={handleLogin}>Login</button>
      )}
    </div>
  );
}
```

---

## TypeScript Types

All API types are defined in `lib/types/api.ts` and match the backend Pydantic schemas:

```typescript
import { CompanySearchResponse, AnalysisResult, User } from '@/lib/types/api';
```

---

## Phase 6 Milestones

### Milestone 6.1: Next.js Setup ✅
- ✅ Next.js 15 installed with TypeScript
- ✅ Tailwind CSS configured
- ✅ App Router structure created
- ✅ Dependencies installed

### Milestone 6.2: API Integration ✅
- ✅ Axios client configured
- ✅ TypeScript types defined
- ✅ Authentication hook created
- ✅ Environment variables set

### Milestone 6.3: Authentication Pages (Next)
- ⏳ Login page
- ⏳ Signup page
- ⏳ Protected routes

### Milestone 6.4: Dashboard Layout (Next)
- ⏳ Header component
- ⏳ Sidebar navigation
- ⏳ Dashboard layout
- ⏳ Footer component

---

## Next Steps

1. Create authentication pages (`app/(auth)/login/page.tsx`)
2. Build dashboard layout (`app/(dashboard)/layout.tsx`)
3. Add header and sidebar components
4. Implement protected routes
5. Create landing page

---

## Backend API Endpoints

The frontend connects to these backend endpoints:

### Authentication
- `POST /api/v1/auth/signup` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user

### Companies
- `GET /api/v1/companies/search` - Search companies
- `GET /api/v1/companies/{id}` - Get company details
- `GET /api/v1/companies/{id}/reports` - Get company reports

### Reports
- `POST /api/v1/reports/upload` - Upload PDF
- `GET /api/v1/reports` - List reports
- `GET /api/v1/reports/{id}` - Get report details
- `DELETE /api/v1/reports/{id}` - Delete report

### Analysis
- `POST /api/v1/analysis/analyze/{report_id}` - Start analysis
- `GET /api/v1/analysis/task/{task_id}` - Get task status
- `GET /api/v1/analysis/{id}` - Get analysis result
- `GET /api/v1/analysis/report/{report_id}` - Get analysis by report
- `GET /api/v1/analysis/{id}/flags` - Get red flags

---

## Development Notes

- All components use TypeScript for type safety
- API calls are strongly typed
- Authentication is handled automatically via axios interceptors
- Token stored in localStorage
- Auto-logout on 401 responses

---

## Production Build

```bash
npm run build
npm run start
```

The app will be available on http://localhost:3000

---

**Phase**: 6/15
**Status**: In Progress
**Last Updated**: February 6, 2026
