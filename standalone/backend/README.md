# RedFlags Standalone Backend

Standalone FastAPI backend for PDF analysis with 42 red flags detection.

## Architecture

### Services

1. **FinEdgeService** (`services/finedge_service.py`)
   - Fetches financial data from FinEdge API
   - Calculates 14 financial data-based flags
   - Categories: Cash Flow (8), Promoter (3), Balance Sheet (3), Revenue Quality (1)

2. **GeminiService** (`services/gemini_service.py`)
   - Analyzes PDF using Google Gemini 2.0 Flash
   - Extracts 28 qualitative flags from annual report
   - Categories: Auditor (6), Related Party (7), Promoter (3), Governance (4), Balance Sheet (4), Revenue Quality (2), Textual (1)

3. **FlagEngine** (`services/flag_engine.py`)
   - Orchestrates FinEdge and Gemini services
   - Combines all 42 flags
   - Handles partial failures gracefully

4. **RiskCalculator** (`services/risk_calculator.py`)
   - Calculates composite risk score (0-100)
   - Uses category weights and severity multipliers
   - Returns risk level: LOW, MODERATE, ELEVATED, HIGH, CRITICAL

### Flag Categories & Weights

- **Auditor**: 20% (6 flags from Gemini)
- **Cash Flow**: 18% (8 flags from FinEdge)
- **Related Party**: 15% (7 flags from Gemini)
- **Promoter**: 15% (3 FinEdge + 3 Gemini = 6 flags)
- **Governance**: 12% (4 flags from Gemini)
- **Balance Sheet**: 10% (3 FinEdge + 4 Gemini = 7 flags)
- **Revenue Quality**: 5% (1 FinEdge + 2 Gemini = 3 flags)
- **Textual Analysis**: 5% (1 flag from Gemini)

### Severity Points

- **CRITICAL**: 25 points (×1.0 multiplier)
- **HIGH**: 15 points (×0.75 multiplier)
- **MEDIUM**: 8 points (×0.5 multiplier)
- **LOW**: 3 points (×0.25 multiplier)

## API Endpoints

### POST /api/upload
Upload PDF and trigger analysis.

**Request:**
- Content-Type: multipart/form-data
- Body: PDF file with filename format `SYMBOL_YEAR.pdf`

**Example filename:** `RELIANCE_2025.pdf`
- Symbol: RELIANCE
- Fiscal Year: 2025 (represents FY 2024-2025)

**Response:**
```json
{
  "analysis_id": "uuid",
  "symbol": "RELIANCE",
  "fiscal_year": 2025,
  "status": "completed",
  "message": "Analysis completed"
}
```

### GET /api/analysis/{analysis_id}
Get analysis results.

**Response:**
```json
{
  "analysis_id": "uuid",
  "status": "completed",
  "symbol": "RELIANCE",
  "fiscal_year": 2025,
  "statement_type": "consolidated",
  "flags": [...],
  "risk_score": {
    "risk_score": 45.2,
    "risk_level": "ELEVATED",
    "risk_description": "...",
    "category_scores": {...},
    "flags_triggered_count": 12,
    "flags_total_count": 42
  }
}
```

### GET /api/health
Health check endpoint.

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Run Server
```bash
python app.py
```

Server starts at: http://localhost:8000

## FinEdge Flags (14 total)

### Cash Flow (8 flags)
- #7: PAT Growing, CFO Flat (HIGH)
- #8: Receivables Growing > Revenue (HIGH)
- #9: Inventory Growing > COGS (HIGH)
- #10: Capex > Depreciation (>3x) (MEDIUM)
- #11: Frequent Exceptional Items (MEDIUM)
- #12: Negative CFO (HIGH)
- #13: CCC > 120 days (MEDIUM)
- #14: Unusual Other Income > 10% (MEDIUM)

### Promoter (3 flags)
- #22: Promoter Pledge > 50% (CRITICAL)
- #23: Promoter Pledge Increasing QoQ (HIGH)
- #24: Promoter Selling Shares (MEDIUM)

### Balance Sheet (3 flags)
- #32: Debt Growing Faster than Equity (HIGH)
- #33: Interest Coverage < 2x (HIGH)
- #38: Intangible Assets Growing Fast (MEDIUM)

### Revenue Quality (1 flag)
- #39: Revenue Concentrated in Q4 (>40%) (MEDIUM)

## Gemini Flags (28 total)

### Auditor (6 flags)
- #1: Auditor Resignation Mid-Term (CRITICAL)
- #2: Qualified/Adverse/Disclaimer Opinion (CRITICAL)
- #3: Emphasis of Matter Paragraph (HIGH)
- #4: Going Concern Issue (CRITICAL)
- #5: KAM on Revenue Recognition (HIGH)
- #6: Audit Fees Declining (MEDIUM)

### Related Party (7 flags)
- #15: RPT > 10% of Revenue (HIGH)
- #16: Loans to Related Parties (HIGH)
- #17: Purchases from RP at Premium (MEDIUM)
- #18: Revenue from RP Increasing (MEDIUM)
- #19: Complex Structure > 20 Subsidiaries (MEDIUM)
- #20: Loans to Directors/KMP (HIGH)
- #21: New Related Parties Added (MEDIUM)

### Promoter (3 flags from Gemini)
- #25: Disproportionate Managerial Remuneration (MEDIUM)
- #26: Promoter Entity Name Change (LOW)
- #27: ICDs to Promoter Group (HIGH)

### Governance (4 flags)
- #28: Independent Director Resignation (HIGH)
- #29: Related Party on Audit Committee (MEDIUM)
- #30: SEBI/Stock Exchange Penalties (HIGH)
- #31: Whistle-blower Complaints (MEDIUM)

### Balance Sheet (4 flags from Gemini)
- #34: Short-term Debt > 60% of Total (HIGH)
- #35: Contingent Liabilities > 20% NW (HIGH)
- #36: Frequent Debt Restructuring (MEDIUM)
- #37: Heavy Asset Pledging (MEDIUM)

### Revenue Quality (2 flags from Gemini)
- #40: Revenue Recognition Policy Changed (HIGH)
- #41: Unbilled Revenue Growing Faster (MEDIUM)

### Textual Analysis (1 flag)
- #42: MD&A Tone is Defensive (MEDIUM)

## Error Handling

### Symbol Validation
- Validates symbol against `finedge/stock_symbol_api.txt`
- Returns 400 if symbol not found

### API Failures
- FinEdge API failure: Returns partial results (Gemini flags only)
- Gemini API failure: Returns partial results (FinEdge flags only)
- Both fail: Returns error with empty flag list

### PDF Parsing
- Invalid filename: Returns 400 with clear error message
- Large file (>50MB): Returns 400

## Logging

All operations are logged with timestamps:
- API calls to FinEdge and Gemini
- Flag calculations
- Errors with stack traces

Check console output for detailed logs.

## Troubleshooting

### Issue: Gemini API error
**Solution:** Check API key in `.env` file. Ensure you have quota available.

### Issue: FinEdge returns empty data
**Solution:** Symbol might not have data available. Try a different symbol.

### Issue: Risk score is 0
**Solution:** Check if any flags were calculated. Review error logs.

### Issue: PDF upload fails
**Solution:** 
- Check filename format: `SYMBOL_YEAR.pdf`
- Ensure file size < 50MB
- Verify PDF is not corrupted

## Development

### Adding New Flags
1. Add flag definition to appropriate service
2. Update category weights if needed
3. Update flag count in documentation
4. Test with real annual reports

### Testing
Test with real PDFs:
```bash
# Example: Test with Reliance FY2025 report
# Filename: RELIANCE_2025.pdf
curl -X POST http://localhost:8000/api/upload \
  -F "file=@RELIANCE_2025.pdf"
```

## Notes
- This is a testing/validation app, not for production
- No database required - results stored in memory
- Results are lost on server restart
- Consolidated statements are prioritized over standalone
