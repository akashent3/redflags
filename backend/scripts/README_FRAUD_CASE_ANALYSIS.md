# Fraud Case Analysis Script

## Overview
This script analyzes historical fraud case PDFs and stores the results in the PostgreSQL database for pattern matching with new analyses.

## Requirements
- PostgreSQL database with `fraud_cases` table created
- R2 storage credentials configured
- FinEdge API access (optional - for symbol data)
- Gemini AI API key configured
- Python dependencies installed

## Usage

### Basic Usage
```bash
python scripts/analyze_fraud_case.py \
    --symbol SATYAM \
    --pdf path/to/satyam_2009.pdf \
    --year 2009 \
    --fraud-type "Accounting Fraud" \
    --stock-decline -97.4 \
    --market-cap-lost 14000
```

### Arguments

**Required:**
- `--symbol` - Company stock symbol (used for FinEdge API lookup)
- `--pdf` - Path to the annual report PDF file
- `--year` - Year of the fraud case (e.g., 2009)
- `--fraud-type` - Type of fraud (e.g., "Accounting Fraud", "Insider Trading")
- `--stock-decline` - Stock price decline percentage (e.g., -97.4)
- `--market-cap-lost` - Market cap lost in crores (e.g., 14000)

**Optional:**
- `--sector` - Company sector (e.g., "IT Services", "Banking")
- `--skip-api` - Skip FinEdge API data fetching (use only PDF analysis)

## Pipeline

The script follows this pipeline:

1. **PDF Upload to R2**
   - Uploads PDF to `fraud_cases/{year}/{company}.pdf`
   - Returns public URL for storage

2. **FinEdge Data Fetch** (optional)
   - Fetches financial data from FinEdge API
   - Calculates 21 non-bank OR 8 bank API-based flags

3. **Gemini PDF Analysis**
   - Analyzes PDF with Gemini AI
   - Extracts 23 non-bank OR 25 bank PDF-based flags

4. **Combine & Save**
   - Combines API flags + PDF flags
   - Calculates total triggered flags
   - Saves to PostgreSQL `fraud_cases` table

## Examples

### Satyam Fraud Case (2009)
```bash
python scripts/analyze_fraud_case.py \
    --symbol SATYAM \
    --pdf data/fraud_cases/satyam_2009.pdf \
    --year 2009 \
    --fraud-type "Accounting Fraud" \
    --sector "IT Services" \
    --stock-decline -97.4 \
    --market-cap-lost 14000
```

### Kingfisher Airlines (2012)
```bash
python scripts/analyze_fraud_case.py \
    --symbol KINGFISHER \
    --pdf data/fraud_cases/kingfisher_2012.pdf \
    --year 2012 \
    --fraud-type "Debt Default" \
    --sector "Aviation" \
    --stock-decline -95.2 \
    --market-cap-lost 8500
```

### IL&FS Financial Crisis (2018)
```bash
python scripts/analyze_fraud_case.py \
    --symbol ILFS \
    --pdf data/fraud_cases/ilfs_2018.pdf \
    --year 2018 \
    --fraud-type "Debt Default" \
    --sector "Finance" \
    --stock-decline -89.0 \
    --market-cap-lost 91000
```

### DHFL (2019)
```bash
python scripts/analyze_fraud_case.py \
    --symbol DHFL \
    --pdf data/fraud_cases/dhfl_2019.pdf \
    --year 2019 \
    --fraud-type "Loan Default" \
    --sector "Finance" \
    --stock-decline -93.8 \
    --market-cap-lost 30000
```

## Output

### Console Output
```
📊 Starting fraud case analysis for Satyam Computer Services (2009)
📄 Uploading PDF to R2...
✅ PDF uploaded: https://pub-xxx.r2.dev/fraud_cases/2009/satyam-computer-services.pdf

📡 Fetching FinEdge data for symbol: SATYAM
✅ FinEdge data fetched successfully

🧮 Calculating API-based flags...
✅ API flags calculated: 12/21 triggered

🤖 Analyzing PDF with Gemini AI...
✅ PDF analysis complete: 18/23 flags triggered

💾 Saving to database...
✅ Fraud case saved successfully!

Case ID: satyam-computer-services-2009
Total flags triggered: 30
Risk indicators:
  - Rapid revenue growth with declining margins
  - Unexplained cash balances
  - Delayed auditor reports
  - Related party transactions
  ... (and 26 more)
```

### Database Record
```json
{
  "case_id": "satyam-computer-services-2009",
  "company_name": "Satyam Computer Services",
  "year": 2009,
  "sector": "IT Services",
  "fraud_type": "Accounting Fraud",
  "stock_decline_percent": -97.4,
  "market_cap_lost_cr": 14000,
  "red_flags_detected": [
    {
      "flag_number": 1,
      "flag_name": "Rapid Revenue Growth",
      "triggered": true,
      "evidence": "Revenue grew 20% YoY while margins declined"
    },
    ...
  ],
  "pdf_url": "https://pub-xxx.r2.dev/fraud_cases/2009/satyam-computer-services.pdf",
  "created_at": "2025-02-16T10:30:00Z"
}
```

## Troubleshooting

### Error: "Symbol not found in FinEdge API"
**Solution:** Use `--skip-api` flag to analyze only the PDF without fetching financial data.

### Error: "Failed to upload PDF to R2"
**Solution:** Check R2 credentials in `.env` file (CLOUDFLARE_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY)

### Error: "Gemini API key not configured"
**Solution:** Set `GEMINI_API_KEY` in `.env` file

### Error: "Database connection failed"
**Solution:** Verify PostgreSQL credentials in `.env` file (DATABASE_URL)

## Pattern Matching

After adding fraud cases using this script, they will be automatically available for pattern matching via:

```bash
POST /api/v1/fraud-cases/pattern-match/{analysis_id}
```

The pattern matching algorithm uses Jaccard similarity to compare red flags between the historical case and a new analysis.

## Best Practices

1. **PDF Quality:** Use high-quality, text-extractable PDFs (not scanned images)
2. **Accurate Data:** Provide accurate stock decline and market cap loss figures
3. **Sector Classification:** Use consistent sector names for better categorization
4. **Year:** Use the year when fraud was discovered, not when it occurred
5. **Multiple Cases:** Analyze multiple historical cases for better pattern matching

## Maintenance

### View All Fraud Cases
```bash
GET /api/v1/fraud-cases/
```

### Delete Fraud Case
```bash
DELETE /api/v1/admin/fraud-cases/{case_id}
```
(Requires admin access)

## Support

For issues or questions, check:
- `backend/app/models/fraud_case.py` - Model definition
- `backend/app/api/v1/fraud_cases.py` - API endpoints
- `backend/sql/create_fraud_cases_table.sql` - Database schema
