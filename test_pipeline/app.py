"""
RedFlag AI — Standalone Test Pipeline
PDF → Section Detection → PDF Slicing → Gemini Flash → 54 Red Flags → Risk Score

Usage:
    1. Set GEMINI_API_KEY environment variable
    2. pip install -r requirements.txt
    3. python app.py
    4. Open http://localhost:8000
"""

import json
import logging
import os
import sys
import time
from typing import Dict, List

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("redflags-test")

# Add current dir to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import pipeline components
from pipeline.pdf_extractor import pdf_extractor
from pipeline.section_detector import section_detector
from pipeline.gemini_analyzer import GeminiAnalyzer

# Import scoring
from scoring.risk_calculator import risk_calculator

# Import all red flag modules (registers them in flag_registry)
from red_flags.registry import flag_registry
import red_flags.auditor_flags
import red_flags.cashflow_flags
import red_flags.related_party_flags
import red_flags.promoter_flags
import red_flags.governance_flags
import red_flags.balance_sheet_flags
import red_flags.revenue_flags
import red_flags.textual_flags

# FastAPI app
app = FastAPI(title="RedFlag AI - Test Pipeline", version="2.0.0")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

# Initialize Gemini
gemini = None
try:
    gemini = GeminiAnalyzer()
    logger.info("Gemini Flash initialized successfully")
except Exception as e:
    logger.error(f"Gemini init failed: {e}. Set GEMINI_API_KEY env variable.")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render upload page."""
    flag_count = flag_registry.get_flag_count()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "flag_count": flag_count,
        "gemini_ready": gemini is not None,
    })


@app.post("/analyze")
async def analyze_pdf(file: UploadFile = File(...)):
    """
    Full pipeline: PDF → Section Detection → Gemini Analysis → 54 Red Flags → Risk Score
    """
    if not gemini:
        return JSONResponse(
            status_code=500,
            content={"error": "Gemini not initialized. Set GEMINI_API_KEY."},
        )

    total_start = time.time()
    steps = {}

    try:
        # Read PDF bytes
        pdf_bytes = await file.read()
        logger.info(f"Received PDF: {file.filename} ({len(pdf_bytes):,} bytes)")

        # ─── STEP 1: PDF Text Extraction (PyMuPDF) ───
        t0 = time.time()
        extraction = pdf_extractor.extract_from_bytes(pdf_bytes)
        pages_data = extraction["pages"]
        total_pages = extraction["total_pages"]
        steps["1_text_extraction"] = {
            "time_seconds": round(time.time() - t0, 2),
            "total_pages": total_pages,
            "total_chars": sum(p["char_count"] for p in pages_data),
        }
        logger.info(f"Step 1: Extracted text from {total_pages} pages in {steps['1_text_extraction']['time_seconds']}s")

        # ─── STEP 2: Section Detection (4-Layer Regex) ───
        t1 = time.time()
        sections = section_detector.detect_sections(pages_data, total_pages)
        steps["2_section_detection"] = {
            "time_seconds": round(time.time() - t1, 2),
            "sections_found": list(sections.keys()),
            "section_pages": {k: v for k, v in sections.items()},
        }
        logger.info(f"Step 2: Detected {len(sections)} sections in {steps['2_section_detection']['time_seconds']}s")

        # If very few sections found, try LLM fallback
        required_sections = ["auditor_report", "balance_sheet", "notes_to_accounts"]
        missing_required = [s for s in required_sections if s not in sections]
        if missing_required and len(sections) < 4:
            logger.warning(f"Missing required sections: {missing_required}. Trying LLM fallback...")
            sample_pages = ""
            sample_indices = list(range(0, min(20, total_pages))) + list(range(max(0, total_pages//2 - 5), min(total_pages, total_pages//2 + 5)))
            for i in sorted(set(sample_indices)):
                if i < len(pages_data):
                    sample_pages += f"--- Page {i+1} ---\n{pages_data[i]['text'][:800]}\n\n"
            fallback = gemini.detect_sections_fallback(pdf_bytes, sample_pages, total_pages)
            if fallback:
                for k, v in fallback.items():
                    if k not in sections and isinstance(v, dict) and "start" in v:
                        sections[k] = v
                logger.info(f"LLM fallback added {len(fallback)} sections")

        # ─── STEP 3: Extract Section Texts ───
        t2 = time.time()
        section_texts = {}
        for section_name in sections:
            text = section_detector.extract_section_text(section_name, sections, pages_data)
            if text:
                section_texts[section_name] = text
        steps["3_section_texts"] = {
            "time_seconds": round(time.time() - t2, 2),
            "sections_with_text": len(section_texts),
        }

        # ─── STEP 4: PDF Slicing ───
        t3 = time.time()
        relevant_pages = section_detector.get_relevant_pages(sections)
        sliced_pdf_bytes = pdf_extractor.slice_pdf(pdf_bytes, relevant_pages)
        steps["4_pdf_slicing"] = {
            "time_seconds": round(time.time() - t3, 2),
            "original_pages": total_pages,
            "sliced_pages": len(relevant_pages),
            "sliced_size_kb": round(len(sliced_pdf_bytes) / 1024, 1),
        }
        logger.info(f"Step 4: Sliced {total_pages} → {len(relevant_pages)} pages ({len(sliced_pdf_bytes)//1024}KB)")

        # ─── STEP 5: Gemini Flash Analysis (3 calls) ───
        t4 = time.time()
        sections_desc = "Sections found:\n"
        for sec_name, pr in sections.items():
            sections_desc += f"  - {sec_name}: pages {pr['start']}-{pr['end']}\n"

        # Build financial summary for textual analysis
        financial_summary = "Not yet available (will use data from Call 1)"

        gemini_results = gemini.analyze_pdf(
            sliced_pdf_bytes,
            sections_description=sections_desc,
            financial_summary=financial_summary,
        )
        steps["5_gemini_analysis"] = {
            "time_seconds": round(time.time() - t4, 2),
            "model": gemini.model_name,
            "has_financial_data": bool(gemini_results.get("financial_data")),
            "has_textual_analysis": bool(gemini_results.get("textual_analysis")),
        }
        logger.info(f"Step 5: Gemini analysis in {steps['5_gemini_analysis']['time_seconds']}s")

        # ─── STEP 6: Run 54 Red Flag Checks ───
        t5 = time.time()

        # Build data dict that flags expect
        flag_data = {
            "sections": section_texts,
            "financial_data": gemini_results.get("financial_data", {}),
            "textual_analysis": gemini_results.get("textual_analysis", {}),
            "extraction_result": extraction,
            "company_name": file.filename.replace(".pdf", ""),
        }

        all_flags = flag_registry.get_all_flags()
        flag_results = []
        for flag_checker in all_flags:
            try:
                result = flag_checker.check(flag_data)
                flag_results.append(result)
            except Exception as e:
                logger.error(f"Flag #{flag_checker.flag_number} failed: {e}")
                flag_results.append(flag_checker.create_not_triggered_result(f"Error: {e}"))

        steps["6_red_flags"] = {
            "time_seconds": round(time.time() - t5, 2),
            "total_flags": len(flag_results),
            "triggered": sum(1 for f in flag_results if f.is_triggered),
        }
        logger.info(f"Step 6: {steps['6_red_flags']['triggered']}/{len(flag_results)} flags triggered in {steps['6_red_flags']['time_seconds']}s")

        # ─── STEP 7: Calculate Risk Score ───
        t6 = time.time()
        risk_result = risk_calculator.calculate_risk_score(flag_results)
        steps["7_risk_score"] = {
            "time_seconds": round(time.time() - t6, 2),
        }

        total_time = round(time.time() - total_start, 2)

        # Build response
        flags_detail = []
        for f in flag_results:
            flags_detail.append({
                "flag_number": f.flag_number,
                "flag_name": f.flag_name,
                "category": f.category.value,
                "severity": f.severity.value,
                "is_triggered": f.is_triggered,
                "confidence": f.confidence_score,
                "evidence": f.evidence_text,
                "detection_method": f.detection_method,
            })

        return JSONResponse(content={
            "success": True,
            "filename": file.filename,
            "total_time_seconds": total_time,
            "pipeline_steps": steps,
            "risk_score": risk_result,
            "flags": flags_detail,
            "sections_detected": {k: v for k, v in sections.items()},
            "financial_data_preview": _preview_financial_data(gemini_results.get("financial_data", {})),
        })

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "pipeline_steps": steps},
        )


def _preview_financial_data(fd: Dict) -> Dict:
    """Create a preview of key financial metrics for display."""
    preview = {}
    pl = fd.get("profit_loss", {})
    bs = fd.get("balance_sheet", {})
    cf = fd.get("cash_flow", {})

    def safe_get(d, *keys):
        current = d
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key, {})
            else:
                return None
        if isinstance(current, dict):
            return current.get("value", current) if "value" in current else None
        return current

    preview["revenue"] = safe_get(pl, "revenue")
    preview["net_profit"] = safe_get(pl, "net_profit")
    preview["cfo"] = safe_get(cf, "cash_from_operations")
    preview["total_debt"] = safe_get(bs, "total_debt")
    preview["equity"] = safe_get(bs, "shareholders_equity")
    preview["total_assets"] = safe_get(bs, "total_assets")

    return {k: v for k, v in preview.items() if v is not None}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting RedFlag AI Test Pipeline on port {port}")
    logger.info(f"Registered {flag_registry.get_flag_count()} red flags")
    logger.info(f"Gemini: {'Ready' if gemini else 'NOT CONFIGURED - set GEMINI_API_KEY'}")
    uvicorn.run(app, host="0.0.0.0", port=port)
