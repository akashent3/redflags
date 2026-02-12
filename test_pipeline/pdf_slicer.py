import os
import sys
import argparse
import logging

# Ensure the script can find the pipeline modules in the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from pipeline.pdf_extractor import pdf_extractor
    from pipeline.section_detector import section_detector
except ImportError as e:
    print(f"Error importing pipeline modules: {e}")
    print("Make sure you place this script inside the 'test_pipeline' folder.")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("pdf-slicer")

def slice_single_pdf(input_path: str, output_path: str):
    """
    Reads a PDF, detects sections, slices it, and saves the result.
    """
    if not os.path.exists(input_path):
        logger.error(f"Input file not found: {input_path}")
        return

    logger.info(f"Reading PDF: {input_path}")
    
    try:
        with open(input_path, "rb") as f:
            pdf_bytes = f.read()

        # 1. Extract Text
        logger.info("Step 1: Extracting text from PDF...")
        extraction = pdf_extractor.extract_from_bytes(pdf_bytes)
        pages_data = extraction["pages"]
        total_pages = extraction["total_pages"]
        logger.info(f"  - Extracted text from {total_pages} pages")
        
        # 2. Detect Sections
        logger.info("Step 2: Detecting relevant sections...")
        sections = section_detector.detect_sections(pages_data, total_pages)
        
        if not sections:
            logger.warning("  ! No specific sections detected (regex failed).")
            logger.warning("  ! The output PDF might be empty or require manual checking.")
        else:
            logger.info(f"  - Detected {len(sections)} sections:")
            for name, limits in sections.items():
                print(f"    • {name}: Pages {limits['start']}-{limits['end']}")

        # 3. Identify Relevant Pages (Union of all detected sections)
        relevant_pages = section_detector.get_relevant_pages(sections)
        
        if not relevant_pages:
            logger.error("No relevant pages found to slice.")
            return

        # 4. Slice PDF
        logger.info(f"Step 3: Slicing PDF to {len(relevant_pages)} pages...")
        sliced_bytes = pdf_extractor.slice_pdf(pdf_bytes, relevant_pages)

        # 5. Save Output
        with open(output_path, "wb") as f:
            f.write(sliced_bytes)
        
        original_size_kb = len(pdf_bytes) / 1024
        new_size_kb = len(sliced_bytes) / 1024
        logger.info("-" * 40)
        logger.info(f"SUCCESS: Saved to {output_path}")
        logger.info(f"Original Size: {original_size_kb:.1f} KB")
        logger.info(f"Sliced Size:   {new_size_kb:.1f} KB")
        logger.info(f"Reduction:     {100 - (new_size_kb/original_size_kb*100):.1f}%")

    except Exception as e:
        logger.error(f"Failed to process PDF: {e}", exc_info=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract relevant sections (Financials, MD&A, Governance) from an Annual Report PDF."
    )
    parser.add_argument("input_pdf", help="Path to the source PDF file")
    parser.add_argument("output_pdf", help="Path to save the sliced PDF")
    
    args = parser.parse_args()
    
    slice_single_pdf(args.input_pdf, args.output_pdf)