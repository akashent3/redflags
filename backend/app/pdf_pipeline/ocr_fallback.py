"""OCR fallback using Surya OCR or Google Vision API."""

import logging
from typing import Optional

from PIL import Image

logger = logging.getLogger(__name__)

# Try importing Surya OCR (optional dependency)
try:
    from surya.ocr import run_ocr
    from surya.model.detection.segformer import load_model as load_det_model
    from surya.model.recognition.model import load_model as load_rec_model

    SURYA_AVAILABLE = True
    logger.info("Surya OCR is available")
except ImportError:
    SURYA_AVAILABLE = False
    logger.warning("Surya OCR not installed. Falling back to Google Vision API.")


def extract_text_with_ocr(image: Image.Image) -> str:
    """
    Extract text from an image using OCR.

    Tries Surya OCR first, falls back to Google Vision API.

    Args:
        image: PIL Image object

    Returns:
        Extracted text

    Raises:
        Exception: If all OCR methods fail
    """
    # Try Surya OCR first
    if SURYA_AVAILABLE:
        try:
            return _extract_with_surya(image)
        except Exception as e:
            logger.error(f"Surya OCR failed: {e}. Trying Google Vision...")

    # Fallback to Google Vision
    try:
        return _extract_with_google_vision(image)
    except Exception as e:
        logger.error(f"Google Vision OCR failed: {e}")
        raise Exception("All OCR methods failed")


def _extract_with_surya(image: Image.Image) -> str:
    """
    Extract text using Surya OCR.

    Args:
        image: PIL Image object

    Returns:
        Extracted text
    """
    try:
        # Load models (cached after first load)
        det_model = load_det_model()
        rec_model = load_rec_model()

        # Run OCR
        predictions = run_ocr([image], [["en"]], det_model, rec_model)

        # Extract text from predictions
        if predictions and len(predictions) > 0:
            prediction = predictions[0]

            # Combine all text lines
            text_lines = []
            for text_line in prediction.text_lines:
                text_lines.append(text_line.text)

            extracted_text = "\n".join(text_lines)
            logger.info(f"Surya OCR extracted {len(extracted_text)} characters")
            return extracted_text
        else:
            logger.warning("Surya OCR returned no predictions")
            return ""

    except Exception as e:
        logger.error(f"Surya OCR extraction failed: {e}", exc_info=True)
        raise


def _extract_with_google_vision(image: Image.Image) -> str:
    """
    Extract text using Google Vision API.

    Args:
        image: PIL Image object

    Returns:
        Extracted text

    Raises:
        Exception: If Google Vision API is not configured or fails
    """
    try:
        from google.cloud import vision
        from io import BytesIO
        from app.config import settings

        if not settings.google_vision_api_key:
            raise Exception("Google Vision API key not configured")

        # Initialize Vision API client
        client = vision.ImageAnnotatorClient()

        # Convert PIL Image to bytes
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)

        # Create Vision API image object
        vision_image = vision.Image(content=img_byte_arr.read())

        # Perform text detection
        response = client.text_detection(image=vision_image)

        if response.error.message:
            raise Exception(f"Google Vision API error: {response.error.message}")

        # Extract full text
        texts = response.text_annotations
        if texts:
            extracted_text = texts[0].description
            logger.info(f"Google Vision OCR extracted {len(extracted_text)} characters")
            return extracted_text
        else:
            logger.warning("Google Vision OCR returned no text")
            return ""

    except ImportError:
        raise Exception("Google Cloud Vision library not installed")
    except Exception as e:
        logger.error(f"Google Vision OCR extraction failed: {e}", exc_info=True)
        raise


def is_ocr_available() -> dict:
    """
    Check which OCR methods are available.

    Returns:
        Dict with availability status of each OCR method
    """
    from app.config import settings

    surya_available = SURYA_AVAILABLE
    google_vision_available = bool(settings.google_vision_api_key)

    return {
        "surya": surya_available,
        "google_vision": google_vision_available,
        "any_available": surya_available or google_vision_available,
    }
