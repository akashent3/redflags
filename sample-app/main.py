import os
import shutil
import json
from typing import List
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# Import the updated pipeline
# CRITICAL: Ensure gemini_pipeline.py is in the same directory as this file
from gemini_pipeline import GeminiRedFlagPipeline

app = FastAPI()

# Setup directories
UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount templates
templates = Jinja2Templates(directory="templates")

# Initialize Pipeline
# Using gemini-1.5-pro for better analysis of large documents
pipeline = GeminiRedFlagPipeline(model_name="models/gemini-2.5-flash") 

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze")
async def analyze_reports(files: List[UploadFile] = File(...)):
    saved_paths = []
    
    try:
        # 1. Save uploaded files
        for file in files:
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_paths.append(file_path)

        # 2. Run Pipeline
        if not saved_paths:
            return JSONResponse({"error": "No files uploaded"}, status_code=400)
            
        # Analyze using the pipeline imported from gemini_pipeline.py
        result = pipeline.analyze(saved_paths)
        
        # 3. Format Output
        response_data = {
            "risk_score": result.risk_score,
            "risk_level": result.risk_level,
            "summary": result.summary,
            "category_scores": result.category_breakdown,
            "flags": result.flags,
            "financial_data": result.financial_data
        }
        
        return JSONResponse(response_data)

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    
    finally:
        # Cleanup uploaded files to save space
        for path in saved_paths:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass

if __name__ == "__main__":
    import uvicorn
    print("Starting RedFlags Mini App on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)