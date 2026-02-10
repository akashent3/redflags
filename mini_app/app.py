"""RedFlag AI Mini App - FastAPI orchestrator.

Analyzes Indian company annual reports for financial red flags using:
1. FinEdge API for up to 21 numerical flags (instant, accurate)
2. Gemini 2.5 Flash for 23 PDF-based flags (single prompt)
3. Weighted risk scoring across 8 categories
4. Sector-based flag filtering for banks/NBFCs/financial services
"""

import json
import logging
import os
import shutil
import tempfile
import time
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from api_flags import calculate_api_flags
from finedge_client import FinEdgeClient
from gemini_analyzer import analyze_pdf_with_gemini, parse_gemini_flags
from risk_calculator import calculate_risk_score

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="RedFlag AI - Mini App", version="0.2.0")

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Store results in memory for the demo
results_store = {}

# Keywords to identify financial sector companies
FINANCIAL_SECTOR_KEYWORDS = ["bank", "nbfc", "financial services", "housing finance", "insurance"]


def detect_financial_sector(profile: dict) -> bool:
    """Check if a company belongs to financial sector (banks, NBFCs, insurance, etc.)."""
    sector = (profile.get("sector", "") or "").lower()
    industry = (profile.get("industry", "") or "").lower()
    return any(kw in sector or kw in industry for kw in FINANCIAL_SECTOR_KEYWORDS)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyze")
async def analyze(
    request: Request,
    company_name: str = Form(...),
    annual_report: UploadFile = File(...),
):
    """Main analysis endpoint. Runs API flags + Gemini PDF analysis."""
    start_time = time.time()
    errors = []
    api_flags_result = []
    gemini_flags_result = []
    api_data_raw = {}
    gemini_raw = {}
    symbol_info = None
    is_financial = False

    # --- Step 1: Find company symbol via FinEdge API ---
    logger.info(f"Searching for symbol: {company_name}")
    try:
        client = FinEdgeClient()
        symbol_info = client.search_symbol(company_name)
        if not symbol_info:
            errors.append(f"Company '{company_name}' not found in FinEdge database. "
                          f"Try using the NSE symbol (e.g., 'RELIANCE', 'TCS', 'ITC').")
    except Exception as e:
        errors.append(f"FinEdge API connection error: {str(e)}")

    # --- Step 2: Fetch financial data and calculate API flags ---
    if symbol_info:
        symbol = symbol_info["symbol"]
        logger.info(f"Found symbol: {symbol} ({symbol_info['name']})")

        try:
            api_data_raw = client.fetch_all_data(symbol)

            # Detect financial sector from company profile
            profile = api_data_raw.get("profile", {})
            is_financial = detect_financial_sector(profile)
            if is_financial:
                logger.info(f"Financial sector detected: {profile.get('sector', '')} / {profile.get('industry', '')}. "
                            f"Skipping incompatible API flags.")

            api_flags_result = calculate_api_flags(api_data_raw, is_financial_sector=is_financial)
            logger.info(f"API flags calculated: {sum(1 for f in api_flags_result if f['triggered'])} triggered "
                        f"out of {len(api_flags_result)}")
        except Exception as e:
            logger.error(f"API flag calculation error: {e}", exc_info=True)
            errors.append(f"API flag calculation error: {str(e)}")

    # --- Step 3: Save uploaded PDF and analyze with Gemini ---
    pdf_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            shutil.copyfileobj(annual_report.file, tmp)
            pdf_path = tmp.name
        logger.info(f"PDF saved to: {pdf_path}")

        gemini_raw = analyze_pdf_with_gemini(pdf_path, is_financial_sector=is_financial)
        gemini_flags_result = parse_gemini_flags(gemini_raw)
        logger.info(f"Gemini flags: {sum(1 for f in gemini_flags_result if f['triggered'])} triggered "
                    f"out of {len(gemini_flags_result)}")
    except Exception as e:
        logger.error(f"Gemini analysis error: {e}", exc_info=True)
        errors.append(f"Gemini PDF analysis error: {str(e)}")
    finally:
        if pdf_path and os.path.exists(pdf_path):
            os.unlink(pdf_path)

    # --- Step 4: Combine all flags and calculate risk score ---
    all_flags = api_flags_result + gemini_flags_result
    all_flags.sort(key=lambda x: x.get("flag_number", 0))

    risk_score = calculate_risk_score(all_flags) if all_flags else {
        "overall_score": 0, "risk_level": "N/A", "risk_color": "#666",
        "risk_description": "Analysis incomplete", "category_scores": {}, "summary": {}
    }

    elapsed = round(time.time() - start_time, 1)

    # Build response
    sector_label = api_data_raw.get("profile", {}).get("sector", "N/A")
    if is_financial:
        sector_label += " (Financial Sector - reduced API flags)"

    result = {
        "company": {
            "name": symbol_info["name"] if symbol_info else company_name,
            "symbol": symbol_info["symbol"] if symbol_info else "N/A",
            "sector": sector_label,
            "industry": api_data_raw.get("profile", {}).get("industry", "N/A"),
            "statement_type": api_data_raw.get("statement_type", gemini_raw.get("statement_type_used", "N/A")),
            "is_financial_sector": is_financial,
        },
        "risk_score": risk_score,
        "flags": all_flags,
        "api_flags_count": len(api_flags_result),
        "gemini_flags_count": len(gemini_flags_result),
        "errors": errors,
        "elapsed_seconds": elapsed,
    }

    # Store for retrieval
    results_store["latest"] = result

    # Save JSON output
    output_path = BASE_DIR / "output.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    logger.info(f"Results saved to {output_path}")

    return templates.TemplateResponse("index.html", {
        "request": request,
        "result": result,
        "company_name": company_name,
    })


@app.get("/api/results")
async def get_results():
    """Get latest results as JSON."""
    if "latest" in results_store:
        return JSONResponse(results_store["latest"])
    return JSONResponse({"error": "No results yet. Run an analysis first."}, status_code=404)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
