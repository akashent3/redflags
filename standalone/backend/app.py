"""FastAPI application for standalone PDF analysis."""

import logging
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from services.finedge_service import FinEdgeService
from services.gemini_service import GeminiService
from services.flag_engine import FlagEngine

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RedFlags Standalone Testing App",
    description="PDF Analysis Pipeline with 42 Red Flags",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", "50")) * 1024 * 1024  # Convert MB to bytes
ALLOWED_EXTENSIONS = [".pdf"]

# Create upload directory
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Initialize services
try:
    finedge_service = FinEdgeService()
    gemini_service = GeminiService()
    flag_engine = FlagEngine(finedge_service, gemini_service)
    logger.info("Services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {e}")
    raise

# In-memory storage for analysis results (for demo purposes)
analysis_storage: Dict[str, Dict] = {}


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "finedge": "configured" if os.getenv("FINEDGE_API_TOKEN") else "missing_token",
            "gemini": "configured" if os.getenv("GEMINI_API_KEY") else "missing_token",
        }
    }


@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload PDF and trigger analysis.
    
    Filename format: SYMBOL_YEAR.pdf (e.g., RELIANCE_2025.pdf)
    - SYMBOL: Stock symbol (e.g., RELIANCE)
    - YEAR: Fiscal year (e.g., 2025 for FY 2024-2025)
    """
    try:
        # Validate file extension
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only PDF files are allowed."
            )
        
        # Parse filename
        symbol, fiscal_year = parse_filename(file.filename)
        
        if not symbol or not fiscal_year:
            raise HTTPException(
                status_code=400,
                detail="Invalid filename format. Expected: SYMBOL_YEAR.pdf (e.g., RELIANCE_2025.pdf)"
            )
        
        # Validate symbol against FinEdge
        if not finedge_service.validate_symbol(symbol):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid stock symbol: {symbol}. Symbol not found in FinEdge database."
            )
        
        # Read file content
        content = await file.read()
        
        # Validate file size
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Generate analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Save PDF to upload directory
        pdf_path = UPLOAD_DIR / f"{analysis_id}.pdf"
        with open(pdf_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"PDF uploaded: {file.filename} -> {analysis_id}")
        
        # Initialize analysis result
        analysis_storage[analysis_id] = {
            "analysis_id": analysis_id,
            "symbol": symbol,
            "fiscal_year": fiscal_year,
            "filename": file.filename,
            "status": "processing",
            "created_at": datetime.now().isoformat(),
            "pdf_path": str(pdf_path)
        }
        
        # Run analysis (synchronous for simplicity)
        try:
            logger.info(f"Starting analysis for {symbol}, FY{fiscal_year}")
            results = flag_engine.analyze(symbol, fiscal_year, str(pdf_path))
            
            # Update storage with results
            analysis_storage[analysis_id].update({
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "results": results
            })
            
            logger.info(f"Analysis completed: {analysis_id}")
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}", exc_info=True)
            analysis_storage[analysis_id].update({
                "status": "failed",
                "error": str(e),
                "completed_at": datetime.now().isoformat()
            })
        
        return {
            "analysis_id": analysis_id,
            "symbol": symbol,
            "fiscal_year": fiscal_year,
            "status": analysis_storage[analysis_id]["status"],
            "message": "Analysis completed" if analysis_storage[analysis_id]["status"] == "completed" else "Analysis failed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """
    Get analysis results by ID.
    
    Returns:
        - status: processing, completed, or failed
        - results: Analysis data including flags and risk score (if completed)
    """
    if analysis_id not in analysis_storage:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    analysis = analysis_storage[analysis_id]
    
    # Return different response based on status
    if analysis["status"] == "processing":
        return {
            "analysis_id": analysis_id,
            "status": "processing",
            "symbol": analysis["symbol"],
            "fiscal_year": analysis["fiscal_year"],
            "created_at": analysis["created_at"]
        }
    
    elif analysis["status"] == "failed":
        return {
            "analysis_id": analysis_id,
            "status": "failed",
            "symbol": analysis["symbol"],
            "fiscal_year": analysis["fiscal_year"],
            "error": analysis.get("error", "Unknown error"),
            "created_at": analysis["created_at"],
            "completed_at": analysis.get("completed_at")
        }
    
    else:  # completed
        results = analysis.get("results", {})
        
        return {
            "analysis_id": analysis_id,
            "status": "completed",
            "symbol": analysis["symbol"],
            "fiscal_year": analysis["fiscal_year"],
            "statement_type": results.get("statement_type", "unknown"),
            "created_at": analysis["created_at"],
            "completed_at": analysis.get("completed_at"),
            "flags": results.get("all_flags", []),
            "risk_score": results.get("risk_score", {}),
            "errors": results.get("errors", []),
            "metadata": {
                "total_flags": len(results.get("all_flags", [])),
                "finedge_flags": len(results.get("finedge_flags", [])),
                "gemini_flags": len(results.get("gemini_flags", [])),
            }
        }


def parse_filename(filename: str) -> tuple:
    """
    Parse PDF filename to extract symbol and fiscal year.
    
    Format: SYMBOL_YEAR.pdf
    Example: RELIANCE_2025.pdf -> ("RELIANCE", 2025)
    
    Returns:
        Tuple of (symbol, fiscal_year) or (None, None) if invalid
    """
    # Remove .pdf extension
    name = filename.replace('.pdf', '').replace('.PDF', '')
    
    # Pattern: SYMBOL_YEAR
    pattern = r'^([A-Z0-9]+)_(\d{4})$'
    match = re.match(pattern, name, re.IGNORECASE)
    
    if match:
        symbol = match.group(1).upper()
        year = int(match.group(2))
        
        # Validate year range (2015-2030)
        if 2015 <= year <= 2030:
            return symbol, year
    
    return None, None


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
