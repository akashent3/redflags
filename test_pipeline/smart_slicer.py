import os
import sys
import json
import logging
import argparse
import time
import zipfile
import io
import re

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from pipeline.pdf_extractor import pdf_extractor
    # Try importing Sarvam, guide user if missing
    try:
        from sarvamai import SarvamAI
    except ImportError:
        print("Error: 'sarvamai' library not found.")
        print("Please install it using: pip install sarvamai")
        sys.exit(1)
except ImportError:
    print("Error: Could not import pipeline modules.")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("sarvam-slicer")

class SarvamAnalyzer:
    def __init__(self):
        self.api_key = os.getenv("SARVAM_API_KEY")
        if not self.api_key:
            raise ValueError("SARVAM_API_KEY environment variable is missing.")
        self.client = SarvamAI(api_subscription_key=self.api_key)

    def extract_document_text(self, pdf_path: str) -> dict:
        """
        Uses Sarvam Document Intelligence to extract text.
        Returns a dictionary mapping page_number (int) -> page_text (str).
        """
        logger.info("Step 1: Uploading to Sarvam Vision AI (Document Intelligence)...")
        
        try:
            # Create Job - Using 'md' as JSON is not supported
            job = self.client.document_intelligence.create_job(
                language="en-IN", 
                output_format="md" 
            )
            
            job.upload_file(pdf_path)
            job.start()
            logger.info(f"  - Job ID: {job.job_id} | Status: Started")
            
            # Wait for completion
            status = job.wait_until_complete()
            
            if status.job_state != "Completed":
                raise Exception(f"Sarvam Job Failed with state: {status.job_state}")
            
            logger.info("  - OCR Completed. Downloading results...")
            zip_content = job.download_output_bytes() 
            
            # Parse ZIP
            return self._parse_sarvam_zip(zip_content)
            
        except Exception as e:
            logger.error(f"Sarvam Vision API Error: {e}")
            raise

    def _parse_sarvam_zip(self, zip_bytes: bytes) -> dict:
        """Extracts page text from the Sarvam output ZIP (Markdown format)."""
        pages_text = {}
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            file_list = z.namelist()
            logger.info(f"  - Files in Sarvam Output: {file_list}")

            # Check for individual page files first (e.g., page_1.txt)
            for fname in file_list:
                if fname.endswith(".txt") or (fname.endswith(".md") and "output" not in fname):
                    nums = re.findall(r'\d+', fname)
                    if nums:
                        p_num = int(nums[-1]) 
                        with z.open(fname) as f:
                            pages_text[p_num] = f.read().decode('utf-8', errors='ignore')
            
            if pages_text:
                return pages_text

            # If no individual files, look for the main output file (output.md)
            md_files = [f for f in file_list if f.endswith(".md")]
            if md_files:
                fname = md_files[0]
                with z.open(fname) as f:
                    content = f.read().decode('utf-8', errors='ignore')
                    
                # Split by Sarvam's delimiter ""
                # This regex captures the page number in the group
                parts = re.split(r'', content)
                
                if len(parts) > 1:
                    # parts[0] is text before the first page marker (often empty or title)
                    # Loop starts at 1. parts[i] is page num, parts[i+1] is text
                    for i in range(1, len(parts), 2):
                        try:
                            p_num = int(parts[i])
                            p_text = parts[i+1]
                            pages_text[p_num] = p_text
                        except (ValueError, IndexError):
                            pass
                else:
                    # No delimiters found, treat entire file as Page 1
                    logger.warning("No page delimiters found. Treating entire text as Page 1.")
                    pages_text[1] = content

        return pages_text

    def verify_section_start(self, text_chunk: str, section_name: str) -> bool:
        """
        Uses Sarvam's LLM to verify if a text chunk is the START of a section.
        """
        prompt = f"""
        Analyze the following text from an Annual Report.
        Determine if this page contains the **start** or **header** of the section: "{section_name}".
        
        Text:
        {text_chunk[:1000]}...
        
        Rules:
        1. It must be the ACTUAL start of the content, not a Table of Contents entry.
        2. Reply ONLY with "YES" or "NO".
        """
        
        try:
            # Using 'sarvam-2.0' (ensure your API key has access)
            response = self.client.chat.completions.create(
                model="sarvam-2.0", 
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10
            )
            answer = response.choices[0].message.content.strip().upper()
            return "YES" in answer
        except Exception as e:
            logger.warning(f"Verification failed: {e}")
            # Fallback: strict keyword matching if LLM fails
            return False

def get_smart_ranges(analyzer, pages_text, total_pages):
    """
    Identifies section ranges by combining Keywords + Sarvam LLM Verification.
    """
    sections_map = {
        "Auditor Report": ["independent auditor's report", "auditor's report"],
        "Directors Report": ["directors' report", "board's report"],
        "MD&A": ["management discussion and analysis", "management discussion & analysis"],
        "Governance": ["corporate governance report", "report on corporate governance"],
        "Balance Sheet": ["balance sheet"],
        "Profit & Loss": ["statement of profit and loss", "profit & loss account"],
        "Cash Flow": ["cash flow statement", "statement of cash flows"],
        "Notes": ["notes to financial statements", "notes to the accounts"]
    }
    
    detected_ranges = {}
    
    # Sort pages to process in order
    sorted_pnums = sorted(pages_text.keys())
    if not sorted_pnums:
        return []

    logger.info("Step 2: Analyzing pages for sections...")
    
    for section, keywords in sections_map.items():
        start_page = None
        
        # Scan pages to find the start
        for p_num in sorted_pnums:
            text = pages_text[p_num].lower()
            
            # 1. Keyword Check
            if any(k in text for k in keywords):
                # 2. AI Verification (Is this actually the start?)
                original_text = pages_text[p_num]
                if analyzer.verify_section_start(original_text, section):
                    start_page = p_num
                    logger.info(f"  • Found {section} start at Page {p_num}")
                    break
        
        if start_page:
            detected_ranges[section] = start_page

    # Construct final list of pages
    pages_to_keep = set()
    sorted_starts = sorted(detected_ranges.values())
    
    for i, start in enumerate(sorted_starts):
        # End is either the next section's start - 1, or end of doc
        if i < len(sorted_starts) - 1:
            end = sorted_starts[i+1] - 1
        else:
            end = min(start + 50, total_pages) # Max 50 pages for the last section
            
        # Add range to set
        for p in range(start, end + 1):
            pages_to_keep.add(p)
            
        # Add buffer
        pages_to_keep.add(max(1, start - 1))
        pages_to_keep.add(min(total_pages, end + 1))
        
    return sorted(list(pages_to_keep))

def smart_slice(input_path, output_path):
    if not os.path.exists(input_path):
        logger.error(f"File not found: {input_path}")
        return

    try:
        analyzer = SarvamAnalyzer()
        
        # 1. Get Text & Layout via Sarvam Vision
        pages_text = analyzer.extract_document_text(input_path)
        
        if not pages_text:
            logger.error("Failed to extract text from Sarvam.")
            return
            
        total_pages = max(pages_text.keys()) if pages_text else 0
        logger.info(f"Analyzed {len(pages_text)} pages (Max Page: {total_pages}).")

        # 2. Identify Sections
        relevant_pages = get_smart_ranges(analyzer, pages_text, total_pages)
        
        if not relevant_pages:
            logger.warning("No sections found. Output might be empty.")
            return

        # 3. Slice using local PDF tool (PyMuPDF) based on Sarvam's findings
        with open(input_path, "rb") as f:
            pdf_bytes = f.read()
            
        logger.info(f"Slicing to keep {len(relevant_pages)} pages...")
        sliced_bytes = pdf_extractor.slice_pdf(pdf_bytes, relevant_pages)
        
        with open(output_path, "wb") as f:
            f.write(sliced_bytes)

        logger.info(f"SUCCESS: Saved sliced PDF to {output_path}")

    except Exception as e:
        logger.error(f"Processing failed: {e}", exc_info=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smart PDF Slicer using Sarvam Vision AI")
    parser.add_argument("input", help="Input PDF file path")
    parser.add_argument("output", help="Output PDF file path")
    args = parser.parse_args()

    smart_slice(args.input, args.output)