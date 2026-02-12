"""Flask server for Gemini Pipeline Test App."""

import os
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from gemini_pipeline import GeminiPipeline

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = '../output'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Initialize Gemini pipeline
pipeline = GeminiPipeline(api_key=os.getenv('GEMINI_API_KEY'))

# In-memory job storage (use Redis/database in production)
jobs = {}


@app.route('/')
def index():
    """Serve the upload page."""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/results.html')
def results_page():
    """Serve the results page."""
    return send_from_directory(app.static_folder, 'results.html')


@app.route('/api/upload', methods=['POST'])
def upload_pdfs():
    """
    Upload 3 annual report PDFs and initiate analysis.
    
    Expects:
        - company_name: str
        - year_1_report: PDF file (oldest)
        - year_2_report: PDF file (middle)
        - year_3_report: PDF file (latest)
        - year_1: str (e.g., "2021")
        - year_2: str (e.g., "2022")
        - year_3: str (e.g., "2023")
    
    Returns:
        - job_id: str
        - status: str
        - message: str
    """
    try:
        # Validate inputs
        if 'company_name' not in request.form:
            return jsonify({'error': 'Company name is required'}), 400
        
        company_name = request.form['company_name']
        
        # Check for all 3 PDFs
        required_files = ['year_1_report', 'year_2_report', 'year_3_report']
        uploaded_files = {}
        
        for file_key in required_files:
            if file_key not in request.files:
                return jsonify({'error': f'{file_key} is required'}), 400
            
            file = request.files[file_key]
            if file.filename == '':
                return jsonify({'error': f'{file_key} has no filename'}), 400
            
            if not file.filename.lower().endswith('.pdf'):
                return jsonify({'error': f'{file_key} must be a PDF file'}), 400
            
            uploaded_files[file_key] = file
        
        # Get years
        years = {
            'year_1': request.form.get('year_1', '2021'),
            'year_2': request.form.get('year_2', '2022'),
            'year_3': request.form.get('year_3', '2023')
        }
        
        # Create job
        job_id = str(uuid.uuid4())
        
        # Save uploaded files temporarily
        pdf_files = {}
        file_info = []
        
        for idx, (file_key, file) in enumerate(uploaded_files.items(), 1):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{job_id}_{filename}")
            file.save(filepath)
            pdf_files[file_key] = filepath
            
            file_info.append({
                "fiscal_year": years[f'year_{idx}'],
                "file_name": filename
            })
        
        # Store job info
        jobs[job_id] = {
            'status': 'processing',
            'company_name': company_name,
            'years': [years['year_1'], years['year_2'], years['year_3']],
            'file_info': file_info,
            'pdf_files': pdf_files,
            'created_at': datetime.now().isoformat(),
            'result': None,
            'error': None
        }
        
        # Start analysis asynchronously (simplified - runs synchronously for now)
        try:
            result = pipeline.analyze_company(
                company_name=company_name,
                pdf_files=[
                    pdf_files['year_1_report'],
                    pdf_files['year_2_report'],
                    pdf_files['year_3_report']
                ],
                years=[years['year_1'], years['year_2'], years['year_3']],
                file_info=file_info
            )
            
            jobs[job_id]['status'] = 'completed'
            jobs[job_id]['result'] = result
            
            # Save to output folder
            output_file = os.path.join(app.config['OUTPUT_FOLDER'], f'{job_id}.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            jobs[job_id]['output_file'] = output_file
            
        except Exception as e:
            jobs[job_id]['status'] = 'failed'
            jobs[job_id]['error'] = str(e)
            return jsonify({
                'job_id': job_id,
                'status': 'failed',
                'error': str(e)
            }), 500
        
        return jsonify({
            'job_id': job_id,
            'status': 'completed',
            'message': 'Analysis completed successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/status/<job_id>', methods=['GET'])
def get_status(job_id):
    """Get job status."""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    return jsonify({
        'job_id': job_id,
        'status': job['status'],
        'error': job.get('error')
    })


@app.route('/api/results/<job_id>', methods=['GET'])
def get_results(job_id):
    """Get analysis results."""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    
    if job['status'] != 'completed':
        return jsonify({
            'error': 'Analysis not completed',
            'status': job['status']
        }), 400
    
    return jsonify(job['result'])


@app.route('/api/download/<job_id>', methods=['GET'])
def download_json(job_id):
    """Download JSON results."""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    
    if job['status'] != 'completed':
        return jsonify({'error': 'Analysis not completed'}), 400
    
    output_file = job.get('output_file')
    if not output_file or not os.path.exists(output_file):
        return jsonify({'error': 'Output file not found'}), 404
    
    return send_from_directory(
        os.path.dirname(output_file),
        os.path.basename(output_file),
        as_attachment=True,
        download_name=f"{job['company_name']}_analysis.json"
    )


if __name__ == '__main__':
    print("=" * 60)
    print("Gemini Pipeline Test App - Server Starting")
    print("=" * 60)
    print(f"Upload UI: http://localhost:5000/")
    print(f"API Endpoint: http://localhost:5000/api/upload")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
