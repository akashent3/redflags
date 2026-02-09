# RedFlags Standalone Testing App

A completely standalone mini-application for testing the PDF → Analysis → Output pipeline with 42 revised red flags. No database required.

## Overview

This app analyzes Indian company annual reports (PDF) and detects 42 accounting red flags across 8 categories using:
- **FinEdge API**: 14 flags based on financial data (P&L, Balance Sheet, Cash Flow)
- **Gemini AI**: 28 flags extracted from PDF (auditor reports, governance, related parties, etc.)

### Why Standalone?

- **Testing & Validation**: Test flag detection logic without full app complexity
- **No Database**: Results stored in memory for simplicity
- **Rapid Iteration**: Quick testing with real annual reports
- **Isolated**: Independent from main application

## Features

✅ Upload PDF with `SYMBOL_YEAR.pdf` format (e.g., `RELIANCE_2025.pdf`)  
✅ Symbol validation against FinEdge stock database  
✅ 14 FinEdge API-based flags (financial metrics)  
✅ 28 Gemini AI-extracted flags (qualitative analysis)  
✅ Risk score calculation (0-100) with weighted categories  
✅ Dashboard UI matching main app design  
✅ Detailed flag evidence with page references  
✅ Error handling for API failures  

## Quick Start

### Prerequisites

- Python 3.9+
- Gemini API key ([Get it here](https://aistudio.google.com/app/apikey))
- Modern web browser

### Setup

1. **Backend Setup**

```bash
cd standalone/backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Run server
python app.py
```

Server starts at: http://localhost:8000

2. **Frontend Setup**

```bash
cd standalone/frontend

# Option 1: Python HTTP server
python -m http.server 8080

# Option 2: Node.js HTTP server (if installed)
npx http-server -p 8080

# Option 3: Any other static file server
```

Frontend accessible at: http://localhost:8080

3. **Use the App**

- Open http://localhost:8080 in your browser
- Upload an annual report PDF with filename: `SYMBOL_YEAR.pdf`
- Wait for analysis (30-60 seconds)
- View results: risk score, flags by category, detailed evidence

## File Naming Convention

**Format:** `SYMBOL_YEAR.pdf`

**Examples:**
- `RELIANCE_2025.pdf` → Reliance Industries, FY 2024-2025
- `TCS_2024.pdf` → TCS, FY 2023-2024
- `INFY_2025.pdf` → Infosys, FY 2024-2025

**Rules:**
- SYMBOL: All caps, matches FinEdge stock symbol
- YEAR: 4-digit fiscal year (2015-2030)
- Must be a valid stock symbol in FinEdge database

## Architecture

```
standalone/
├── backend/
│   ├── app.py                      # FastAPI application
│   ├── services/
│   │   ├── finedge_service.py      # FinEdge API integration (14 flags)
│   │   ├── gemini_service.py       # Gemini AI integration (28 flags)
│   │   ├── flag_engine.py          # Flag aggregation
│   │   ├── risk_calculator.py      # Risk score calculation
│   │   └── models.py               # Data models
│   ├── prompts/
│   │   └── gemini_prompt.txt       # Comprehensive Gemini prompt
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
├── frontend/
│   ├── index.html                  # Main UI
│   ├── script.js                   # Upload & display logic
│   ├── style.css                   # Matching dashboard styles
│   └── assets/
└── README.md                       # This file
```

## 42 Red Flags

### Category Distribution

| Category | FinEdge | Gemini | Total | Weight |
|----------|---------|--------|-------|--------|
| Auditor | 0 | 6 | 6 | 20% |
| Cash Flow | 8 | 0 | 8 | 18% |
| Related Party | 0 | 7 | 7 | 15% |
| Promoter | 3 | 3 | 6 | 15% |
| Governance | 0 | 4 | 4 | 12% |
| Balance Sheet | 3 | 4 | 7 | 10% |
| Revenue Quality | 1 | 2 | 3 | 5% |
| Textual Analysis | 0 | 1 | 1 | 5% |
| **TOTAL** | **14** | **28** | **42** | **100%** |

### Severity Levels

- **CRITICAL**: 9 flags (accounting fraud indicators)
- **HIGH**: 16 flags (serious concerns requiring attention)
- **MEDIUM**: 16 flags (yellow flags worth monitoring)
- **LOW**: 1 flag (minor concern)

## Risk Score Calculation

**Formula:**
```
1. For each category:
   - Calculate points: Σ(triggered flags × severity points × confidence)
   - Normalize: (actual points / max possible points) × 100

2. Weighted score:
   - Σ(category score × category weight)

3. Risk level:
   - 0-20: LOW
   - 20-40: MODERATE
   - 40-60: ELEVATED
   - 60-80: HIGH
   - 80-100: CRITICAL
```

**Severity Points:**
- CRITICAL: 25 points
- HIGH: 15 points
- MEDIUM: 8 points
- LOW: 3 points

## API Endpoints

### POST /api/upload
Upload PDF and trigger analysis.

**Request:** Multipart form-data with PDF file

**Response:**
```json
{
  "analysis_id": "uuid",
  "symbol": "RELIANCE",
  "fiscal_year": 2025,
  "status": "completed"
}
```

### GET /api/analysis/{analysis_id}
Get analysis results.

**Response:** Complete analysis with flags and risk score

### GET /api/health
Health check.

## Configuration

Edit `backend/.env`:

```env
# FinEdge API (pre-configured)
FINEDGE_API_URL=https://data.finedgeapi.com/api/v1
FINEDGE_API_TOKEN=hicmeh4o6heyducv4usdzfz6ar2dsrassmerqrc4jnparnj5ylgps77rxgdfmleuddifs3xxcycpijddc5eq

# Gemini API (you need to add)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=models/gemini-2.0-flash-exp

# App Config
UPLOAD_DIR=./uploads
MAX_FILE_SIZE_MB=50
PORT=8000
```

## Testing

### Test with Real Annual Reports

1. Download annual reports from company websites or BSE/NSE
2. Rename to `SYMBOL_YEAR.pdf` format
3. Upload through UI or API

**Recommended test companies:**
- RELIANCE (Large cap, diversified)
- TCS (IT services, clean books)
- INFY (IT services, international ops)
- TATASTEEL (Manufacturing, cyclical)

### API Testing with curl

```bash
# Upload PDF
curl -X POST http://localhost:8000/api/upload \
  -F "file=@RELIANCE_2025.pdf"

# Get results
curl http://localhost:8000/api/analysis/{analysis_id}

# Health check
curl http://localhost:8000/api/health
```

## Troubleshooting

### Backend won't start
- Check Python version (3.9+)
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check if port 8000 is available

### Frontend can't connect to backend
- Ensure backend is running on port 8000
- Check browser console for CORS errors
- Verify API_BASE_URL in `script.js`

### Invalid symbol error
- Symbol must exist in `finedge/stock_symbol_api.txt`
- Try: RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK

### Gemini API error
- Verify API key in `.env`
- Check quota at https://aistudio.google.com
- Ensure model name is correct

### No flags detected
- Check if PDF is readable (not scanned image)
- Verify it's an Indian company annual report
- Look for errors in backend logs

### Analysis takes too long
- Normal: 30-60 seconds for first analysis
- Gemini API processes entire PDF
- FinEdge fetches 3-5 years of data

## Limitations

⚠️ **Not for Production**
- In-memory storage (results lost on restart)
- No authentication
- No rate limiting
- Single-threaded processing

⚠️ **Data Limitations**
- FinEdge: Some companies may have incomplete data
- Gemini: Accuracy depends on PDF quality and structure
- Promoter flags #22-24: May have limited data from FinEdge

⚠️ **Testing Only**
- Use for validation and testing
- Compare with manual analysis
- Verify flag logic against actual reports

## Differences from Main App

| Feature | Main App | Standalone |
|---------|----------|------------|
| Database | PostgreSQL | In-memory |
| Storage | AWS S3 | Local disk |
| Auth | Required | None |
| Queue | Celery | Synchronous |
| Caching | Redis | None |
| UI | Next.js | Static HTML |
| Deployment | Docker | Local |

## Contributing

This is a testing app. To contribute:

1. Test with various annual reports
2. Report flag detection issues
3. Suggest prompt improvements
4. Document edge cases

## License

Same as main RedFlags application.

## Support

For issues or questions:
1. Check logs in backend console
2. Review this README
3. Check backend/README.md for API details
4. Test with known good PDFs (RELIANCE, TCS)

---

**Note:** This app uses consolidated financial statements when available, falling back to standalone statements only if consolidated are not present.
