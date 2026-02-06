"""
Phase 2 PDF Processing Pipeline - Usage Examples

This file demonstrates how to use the PDF processing pipeline
to analyze annual reports.

Run from backend directory:
    python -m examples.phase2_usage_example
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


async def example_1_basic_extraction():
    """Example 1: Basic PDF text extraction."""
    print("\n=== Example 1: Basic PDF Text Extraction ===\n")

    from app.pdf_pipeline import pdf_extractor

    # Read a PDF file
    pdf_path = Path("sample_annual_report.pdf")

    if not pdf_path.exists():
        print("⚠️  Sample PDF not found. Using mock data.")
        # Create a minimal test PDF
        import fitz

        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((100, 100), "Sample Annual Report\nFiscal Year 2023\n\nAuditor's Report\n...")
        pdf_bytes = doc.tobytes()
        doc.close()
    else:
        pdf_bytes = pdf_path.read_bytes()

    # Extract text
    result = pdf_extractor.extract_from_bytes(pdf_bytes, use_ocr_fallback=True)

    print(f"✓ Extraction complete!")
    print(f"  Total pages: {result['total_pages']}")
    print(f"  Extraction method: {result['extraction_method']}")
    print(f"  Total text length: {len(result['text'])} characters")
    print(f"  First 200 chars: {result['text'][:200]}...")

    return result


async def example_2_section_detection():
    """Example 2: Detect financial statement sections."""
    print("\n=== Example 2: Section Detection ===\n")

    from app.pdf_pipeline import pdf_extractor, section_detector

    # Extract PDF first (reuse from example 1)
    import fitz

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (50, 50),
        """
        Annual Report 2023

        Table of Contents:
        1. Director's Report .................... Page 10
        2. Auditor's Report ..................... Page 25
        3. Balance Sheet ........................ Page 40
        4. Profit & Loss Statement .............. Page 42
        5. Cash Flow Statement .................. Page 44
        6. Notes to Accounts .................... Page 50
    """,
    )
    pdf_bytes = doc.tobytes()
    doc.close()

    result = pdf_extractor.extract_from_bytes(pdf_bytes, use_ocr_fallback=False)

    # Detect sections
    print("🔍 Detecting sections using Gemini AI...")
    sections = section_detector.detect_sections(
        full_text=result["text"], pages_data=result["pages"], total_pages=result["total_pages"]
    )

    print(f"\n✓ Detected {len(sections)} sections:")
    for section_name, page_range in sections.items():
        print(f"  - {section_name}: Pages {page_range['start']}-{page_range['end']}")

    return sections, result


async def example_3_financial_extraction():
    """Example 3: Extract structured financial data."""
    print("\n=== Example 3: Financial Data Extraction ===\n")

    from app.pdf_pipeline import pdf_extractor, section_detector, financial_data_extractor

    # Mock a more complete PDF
    import fitz

    doc = fitz.open()

    # Page 1: Balance Sheet
    page1 = doc.new_page()
    page1.insert_text(
        (50, 50),
        """
        BALANCE SHEET as at March 31, 2023

        Assets:
        Current Assets ................... Rs. 15,000 Cr
        Accounts Receivable .............. Rs. 5,000 Cr
        Inventory ........................ Rs. 3,000 Cr

        Liabilities:
        Total Debt ....................... Rs. 8,000 Cr
        Current Liabilities .............. Rs. 4,000 Cr

        Shareholders' Equity ............. Rs. 20,000 Cr
    """,
    )

    # Page 2: P&L Statement
    page2 = doc.new_page()
    page2.insert_text(
        (50, 50),
        """
        PROFIT & LOSS STATEMENT for the year ended March 31, 2023

        Revenue .......................... Rs. 50,000 Cr
        Operating Profit (EBIT) .......... Rs. 8,000 Cr
        Net Profit (PAT) ................. Rs. 6,000 Cr
    """,
    )

    # Page 3: Cash Flow
    page3 = doc.new_page()
    page3.insert_text(
        (50, 50),
        """
        CASH FLOW STATEMENT for the year ended March 31, 2023

        Cash Flow from Operations ....... Rs. 5,500 Cr
        Cash Flow from Investing ......... Rs. (2,000) Cr
        Cash Flow from Financing ......... Rs. 1,000 Cr
    """,
    )

    pdf_bytes = doc.tobytes()
    doc.close()

    # Extract and detect
    result = pdf_extractor.extract_from_bytes(pdf_bytes, use_ocr_fallback=False)

    # Mock sections (in real use, section_detector would find these)
    section_texts = {
        "balance_sheet": result["pages"][0]["text"],
        "profit_loss_statement": result["pages"][1]["text"],
        "cash_flow_statement": result["pages"][2]["text"],
    }

    print("🧮 Extracting financial data using Gemini AI...")
    financial_data = financial_data_extractor.extract_key_metrics(
        sections=section_texts, fiscal_year="2023"
    )

    print("\n✓ Financial data extracted:")
    print(f"  Fiscal Year: {financial_data['fiscal_year']}")

    if "balance_sheet" in financial_data and "error" not in financial_data["balance_sheet"]:
        print(f"  Balance Sheet: ✓ Extracted")
    if "profit_loss" in financial_data and "error" not in financial_data["profit_loss"]:
        print(f"  P&L Statement: ✓ Extracted")
    if "cash_flow" in financial_data and "error" not in financial_data["cash_flow"]:
        print(f"  Cash Flow: ✓ Extracted")

    return financial_data


async def example_4_r2_storage():
    """Example 4: Upload to and download from R2 storage."""
    print("\n=== Example 4: R2 Storage Operations ===\n")

    from app.storage import r2_client

    # Create a test PDF
    import fitz

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((100, 100), "Test PDF for R2 storage")
    pdf_bytes = doc.tobytes()
    doc.close()

    # Upload to R2
    print("📤 Uploading to R2...")
    object_key = "test/example_report_2023.pdf"
    try:
        public_url = r2_client.upload_file(pdf_bytes, object_key)
        print(f"✓ Upload successful!")
        print(f"  URL: {public_url}")
        print(f"  Size: {len(pdf_bytes)} bytes")

        # Check if file exists
        exists = r2_client.file_exists(object_key)
        print(f"  File exists: {exists}")

        # Get file size
        size = r2_client.get_file_size(object_key)
        print(f"  Remote size: {size} bytes")

        # Download file
        print("\n📥 Downloading from R2...")
        downloaded_bytes = r2_client.download_file(object_key)
        print(f"✓ Download successful!")
        print(f"  Downloaded size: {len(downloaded_bytes)} bytes")
        print(f"  Content matches: {pdf_bytes == downloaded_bytes}")

        # Delete file
        print("\n🗑️  Deleting from R2...")
        deleted = r2_client.delete_file(object_key)
        print(f"✓ Delete successful: {deleted}")

        # Verify deletion
        exists_after = r2_client.file_exists(object_key)
        print(f"  File exists after delete: {exists_after}")

    except Exception as e:
        print(f"✗ R2 operation failed: {e}")
        print("  Check R2 credentials in .env file")


async def example_5_complete_pipeline():
    """Example 5: Complete end-to-end pipeline."""
    print("\n=== Example 5: Complete Pipeline ===\n")

    from app.storage import r2_client
    from app.pdf_pipeline import pdf_extractor, section_detector, financial_data_extractor

    # Step 1: Create or load PDF
    print("📄 Step 1: Loading PDF...")
    import fitz

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (50, 50),
        """
        RELIANCE INDUSTRIES LIMITED
        Annual Report 2023

        Contents:
        - Auditor's Report: Page 12
        - Balance Sheet: Page 45
        - P&L Statement: Page 47
        - Cash Flow: Page 49

        Balance Sheet:
        Total Assets: Rs. 100,000 Cr
        Total Debt: Rs. 30,000 Cr
        Equity: Rs. 60,000 Cr

        P&L Statement:
        Revenue: Rs. 150,000 Cr
        Net Profit: Rs. 15,000 Cr

        Cash Flow:
        CFO: Rs. 12,000 Cr
    """,
    )
    pdf_bytes = doc.tobytes()
    doc.close()
    print(f"✓ PDF created ({len(pdf_bytes)} bytes)")

    # Step 2: Upload to R2
    print("\n📤 Step 2: Uploading to R2...")
    try:
        object_key = "reports/2023/RELIANCE_FY2023.pdf"
        public_url = r2_client.upload_file(pdf_bytes, object_key)
        print(f"✓ Uploaded to: {public_url}")
    except Exception as e:
        print(f"⚠️  R2 upload skipped: {e}")
        object_key = None

    # Step 3: Extract text
    print("\n📝 Step 3: Extracting text...")
    extraction_result = pdf_extractor.extract_from_bytes(pdf_bytes, use_ocr_fallback=False)
    print(f"✓ Extracted {len(extraction_result['text'])} characters from {extraction_result['total_pages']} pages")

    # Step 4: Detect sections
    print("\n🔍 Step 4: Detecting sections...")
    try:
        sections = section_detector.detect_sections(
            full_text=extraction_result["text"],
            pages_data=extraction_result["pages"],
            total_pages=extraction_result["total_pages"],
        )
        print(f"✓ Detected {len(sections)} sections")
    except Exception as e:
        print(f"⚠️  Section detection failed: {e}")
        print("  Using mock sections for demo")
        sections = {
            "balance_sheet": {"start": 1, "end": 1},
            "profit_loss_statement": {"start": 1, "end": 1},
            "cash_flow_statement": {"start": 1, "end": 1},
        }

    # Step 5: Extract financial data
    print("\n🧮 Step 5: Extracting financial data...")
    try:
        section_texts = {
            name: section_detector.extract_section_text(name, sections, extraction_result["pages"])
            for name in sections.keys()
        }
        financial_data = financial_data_extractor.extract_key_metrics(
            sections=section_texts, fiscal_year="2023"
        )
        print(f"✓ Financial data extracted for FY{financial_data['fiscal_year']}")
        print(f"  Extraction status: {financial_data['extraction_status']}")
    except Exception as e:
        print(f"⚠️  Financial extraction failed: {e}")
        financial_data = {"fiscal_year": "2023", "error": str(e)}

    # Step 6: Clean up (delete from R2)
    if object_key:
        print("\n🗑️  Step 6: Cleaning up...")
        try:
            r2_client.delete_file(object_key)
            print(f"✓ Deleted from R2: {object_key}")
        except Exception as e:
            print(f"⚠️  R2 deletion skipped: {e}")

    print("\n✅ Pipeline complete!")

    return {
        "extraction": extraction_result,
        "sections": sections,
        "financial_data": financial_data,
    }


async def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("Phase 2 PDF Processing Pipeline - Usage Examples")
    print("=" * 60)

    # Example 1: Basic extraction
    await example_1_basic_extraction()

    # Example 2: Section detection (requires Gemini API)
    # await example_2_section_detection()

    # Example 3: Financial extraction (requires Gemini API)
    # await example_3_financial_extraction()

    # Example 4: R2 storage (requires R2 credentials)
    # await example_4_r2_storage()

    # Example 5: Complete pipeline (requires all APIs)
    # await example_5_complete_pipeline()

    print("\n" + "=" * 60)
    print("Examples complete!")
    print("\nTo run other examples:")
    print("  1. Uncomment the example function calls above")
    print("  2. Ensure API credentials are set in .env")
    print("  3. Run: python examples/phase2_usage_example.py")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
