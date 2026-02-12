# Gemini Pipeline Test App

Testing the replacement of the current multi-stage Python pipeline with Gemini 2.5 Flash direct PDF processing.

## Overview

This mini application tests the viability of using Gemini 2.5 Flash to:
- Process PDF annual reports directly (no PyMuPDF extraction)
- Extract structured financial data
- Detect all 54 red flags
- Calculate risk scores

**Current Pipeline:**
```
PDF → PyMuPDF → Section Detection (Gemini) → Data Extraction (Gemini) → Red Flags (Rule-based + LLM) → Scoring
```

**New Pipeline (Being Tested):**
```
PDF → Gemini 2.5 Flash (All-in-One) → Red Flags + Scoring → JSON
```

##Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in the `backend/` directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Run the Server

```bash
cd backend
python app.py
```

The app will start at `http://localhost:5000`

### 4. Upload Annual Reports

1. Open `http://localhost:5000` in your browser
2. Enter company name
3. Upload 3 consecutive years of annual report PDFs
4. Click "Analyze with Gemini"
5. View results and download JSON

## Project Structure

```
mini-test-app/
├── backend/
│   ├── app.py                    # Flask server
│   ├── gemini_pipeline.py        # Main Gemini pipeline
│   ├── schema.py                 # JSON schema definitions
│   ├── requirements.txt          # Python dependencies
│   ├── prompts/
│   │   ├── financial_extraction.py    # Financial data extraction
│   │   └── red_flags/
│   │       ├── auditor_flags.py       # 8 auditor flags (detailed)
│   │       ├── cashflow_flags.py      # 8 cashflow flags (detailed)
│   │       └── remaining_flags.py     # 38 remaining flags
│   └── uploads/                  # Temporary PDF storage
├── frontend/
│   ├── index.html               # Upload UI
│   ├── results.html             # Results display
│   ├── style.css                # Styling
│   └── script.js                # Frontend logic
└── output/                      # JSON output files

```

## Features

### ✅ Direct PDF Processing
- Gemini 2.5 Flash processes PDFs without text extraction step
- Eliminates PyMuPDF and OCR dependencies

### ✅ All 54 Red Flags
Organized by category:
- **Auditor** (8 flags): Changes, qualified opinions, going concern, fees, etc.
- **Cash Flow** (8 flags): CFO/PAT divergence, negative CFO, working capital, etc.
- **Related Party** (7 flags): RPT percentages, loans, arm's length pricing
- **Promoter** (6 flags): Pledges, shareholding changes, compensation
- **Governance** (7 flags): Board composition, meetings, internal controls
- **Balance Sheet** (7 flags): D/E ratio, current ratio, receivables, etc.
- **Revenue** (5 flags): Recognition policies, margin decline, concentration
- **Textual** (6 flags): MD&A tone, disclosure quality, contradictions

### ✅ Detailed Prompts for Accuracy
- Specific detection logic for each flag
- Calculation formulas included
- Confidence scoring guidelines
- Examples for model guidance
- Target: 90-95% accuracy

### ✅ Risk Scoring
- Weighted category scores
- 0-100 overall risk score
- Risk levels: LOW, MODERATE, ELEVATED, HIGH, CRITICAL
- Matches current system algorithm

### ✅ JSON Output
- Matches current database schema
- Includes all extracted financial data
- Full flag evidence and page references
- Downloadable for analysis

## API Endpoints

### POST /api/upload
Upload 3 PDF files and initiate analysis

**Form Data:**
- `company_name`: Company name (string)
- `year_1_report`: PDF file (oldest)
- `year_2_report`: PDF file (middle)
- `year_3_report`: PDF file (latest)
- `year_1`, `year_2`, `year_3`: Year strings

**Response:**
```json
{
  "job_id": "uuid",
  "status": "completed",
  "message": "Analysis completed successfully"
}
```

### GET /api/results/:job_id
Get full analysis results

**Response:** Complete JSON matching schema (see output example below)

### GET /api/download/:job_id
Download JSON file

## Output Example

```json
{
  "company": {
    "name": "Example Ltd",
    "analysis_date": "2026-02-08T10:25:00Z"
  },
  "annual_reports": [
    {"fiscal_year": "2021", "file_name": "report_2021.pdf"},
    {"fiscal_year": "2022", "file_name": "report_2022.pdf"},
    {"fiscal_year": "2023", "file_name": "report_2023.pdf"}
  ],
  "analysis_result": {
    "risk_score": 65,
    "risk_level": "HIGH",
    "category_scores": {
      "auditor": 45,
      "cash_flow": 78,
      "related_party": 32,
      ...
    },
    "flags_triggered_count": 18,
    "analyzed_at": "2026-02-08T10:25:00Z"
  },
  "red_flags": [
    {
      "flag_number": 9,
      "flag_name": "Profit growing but CFO flat/declining",
      "category": "CASH_FLOW",
      "severity": "HIGH",
      "is_triggered": true,
      "confidence_score": 92.5,
      "evidence_text": "...",
      "page_references": [45, 67],
      "extracted_data": {...},
      "detection_method": "llm"
    }
    // ... all 54 flags
  ],
  "financial_data": {
    "2021": {...},
    "2022": {...},
    "2023": {...}
  }
}
```

## Evaluation Criteria

### Accuracy Target: 90-95%
1. **Financial Data Extraction**: Compare extracted metrics vs manual verification
2. **Red Flag Detection**: Test on known cases (e.g., Satyam, IL&FS)
3. **False Positive Rate**: Test on clean companies (TCS, Infosys) - target <10%

### Performance
- Processing time: <2 minutes for 3 reports (~750 pages)
- Cost: Monitor Gemini API token usage

### Comparison
Compare output vs current pipeline for same companies to validate equivalence.

## Next Steps

If this test is successful:
1. Integrate into main application
2. Run A/B testing against current pipeline
3. Gradually migrate production traffic
4. Monitor accuracy and cost metrics

## Notes

- This is a **test application** - not for production use
- Runs independently from main RedFlags app
- No database - results stored as JSON files
- Simplified error handling for testing purposes

## License

Internal testing tool for RedFlags AI development.
