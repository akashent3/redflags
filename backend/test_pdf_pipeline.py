"""Test script for Phase 2: PDF Processing Pipeline."""

import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def test_imports():
    """Test that all PDF pipeline modules can be imported."""
    logger.info("Testing imports...")

    try:
        from app.storage.r2_client import r2_client

        logger.info("✓ R2 client imported successfully")
    except Exception as e:
        logger.error(f"✗ Failed to import R2 client: {e}")
        return False

    try:
        from app.pdf_pipeline.extractor import pdf_extractor

        logger.info("✓ PDF extractor imported successfully")
    except Exception as e:
        logger.error(f"✗ Failed to import PDF extractor: {e}")
        return False

    try:
        from app.pdf_pipeline.ocr_fallback import is_ocr_available

        ocr_status = is_ocr_available()
        logger.info(f"✓ OCR fallback imported. Status: {ocr_status}")
    except Exception as e:
        logger.error(f"✗ Failed to import OCR fallback: {e}")
        return False

    try:
        from app.pdf_pipeline.section_detector import section_detector

        logger.info("✓ Section detector imported successfully")
    except Exception as e:
        logger.error(f"✗ Failed to import section detector: {e}")
        return False

    try:
        from app.pdf_pipeline.data_extractor import financial_data_extractor

        logger.info("✓ Financial data extractor imported successfully")
    except Exception as e:
        logger.error(f"✗ Failed to import financial data extractor: {e}")
        return False

    try:
        from app.llm.gemini_client import gemini_client

        logger.info("✓ Gemini client imported successfully")
    except Exception as e:
        logger.error(f"✗ Failed to import Gemini client: {e}")
        return False

    logger.info("\n✓ All imports successful!")
    return True


def test_config():
    """Test that all required config values are set."""
    logger.info("\nTesting configuration...")

    try:
        from app.config import settings

        # Check R2 config
        if not settings.r2_access_key_id or settings.r2_access_key_id == "your-r2-access-key":
            logger.warning("⚠ R2_ACCESS_KEY_ID not configured")
        else:
            logger.info("✓ R2_ACCESS_KEY_ID configured")

        if not settings.r2_bucket_name:
            logger.warning("⚠ R2_BUCKET_NAME not configured")
        else:
            logger.info(f"✓ R2_BUCKET_NAME: {settings.r2_bucket_name}")

        # Check Gemini config
        if not settings.gemini_api_key or settings.gemini_api_key == "your-gemini-api-key":
            logger.warning("⚠ GEMINI_API_KEY not configured")
        else:
            logger.info("✓ GEMINI_API_KEY configured")

        logger.info("\n✓ Configuration check complete")
        return True

    except Exception as e:
        logger.error(f"✗ Configuration test failed: {e}")
        return False


def test_pdf_extraction():
    """Test PDF extraction with a mock PDF."""
    logger.info("\nTesting PDF extraction (with mock data)...")

    try:
        from app.pdf_pipeline.extractor import pdf_extractor
        import fitz  # PyMuPDF

        # Create a minimal test PDF in memory
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((100, 100), "Test Annual Report\nFiscal Year 2023")
        pdf_bytes = doc.tobytes()
        doc.close()

        # Test extraction
        result = pdf_extractor.extract_from_bytes(pdf_bytes, use_ocr_fallback=False)

        assert "text" in result, "Missing 'text' in result"
        assert "pages" in result, "Missing 'pages' in result"
        assert "total_pages" in result, "Missing 'total_pages' in result"
        assert result["total_pages"] == 1, f"Expected 1 page, got {result['total_pages']}"

        logger.info(f"✓ PDF extraction successful: {len(result['text'])} characters extracted")
        logger.info(f"  Extraction method: {result['extraction_method']}")
        return True

    except Exception as e:
        logger.error(f"✗ PDF extraction test failed: {e}", exc_info=True)
        return False


def test_gemini_connection():
    """Test Gemini API connection."""
    logger.info("\nTesting Gemini API connection...")

    try:
        from app.llm.gemini_client import gemini_client

        # Try a simple generation
        response = gemini_client.generate_text(
            prompt="Say 'Hello' if you can read this.",
            max_tokens=50,
            temperature=0.1,
        )

        if response:
            logger.info(f"✓ Gemini API connection successful")
            logger.info(f"  Response: {response[:100]}")
            return True
        else:
            logger.warning("⚠ Gemini returned empty response")
            return False

    except Exception as e:
        logger.error(f"✗ Gemini API test failed: {e}")
        logger.warning("  Make sure GEMINI_API_KEY is set in .env")
        return False


def main():
    """Run all tests."""
    logger.info("=" * 60)
    logger.info("Phase 2: PDF Processing Pipeline - Test Suite")
    logger.info("=" * 60)

    results = {
        "Imports": test_imports(),
        "Configuration": test_config(),
        "PDF Extraction": test_pdf_extraction(),
        "Gemini API": test_gemini_connection(),
    }

    logger.info("\n" + "=" * 60)
    logger.info("Test Results Summary")
    logger.info("=" * 60)

    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        logger.info(f"{test_name}: {status}")

    all_passed = all(results.values())

    if all_passed:
        logger.info("\n✓ All tests passed! Phase 2 implementation is ready.")
    else:
        logger.warning("\n⚠ Some tests failed. Review errors above.")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
