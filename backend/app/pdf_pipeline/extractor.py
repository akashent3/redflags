"""PDF text extraction with PyMuPDF and OCR fallback."""

import logging
from typing import Dict, List, Optional, Tuple

import fitz  # PyMuPDF
from PIL import Image

from app.pdf_pipeline.ocr_fallback import extract_text_with_ocr

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Extract text content from PDF files with OCR fallback."""

    def __init__(self):
        """Initialize PDF extractor."""
        self.min_text_threshold = 50  # Minimum characters to consider extraction successful

    def extract_from_bytes(
        self, pdf_bytes: bytes, use_ocr_fallback: bool = True
    ) -> Dict[str, any]:
        """
        Extract text from PDF bytes.

        Args:
            pdf_bytes: PDF file content as bytes
            use_ocr_fallback: Whether to use OCR if native extraction fails

        Returns:
            Dict containing:
                - text: Full extracted text
                - pages: List of dicts with page-level data
                - metadata: PDF metadata
                - extraction_method: 'native' or 'ocr'
                - total_pages: Number of pages

        Raises:
            Exception: If extraction fails completely
        """
        try:
            # Open PDF from bytes
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            total_pages = len(doc)

            logger.info(f"Processing PDF with {total_pages} pages")

            # Extract metadata
            metadata = self._extract_metadata(doc)

            # Try native text extraction first
            pages_data, full_text = self._extract_native(doc)

            # Check if native extraction was successful
            if len(full_text.strip()) < self.min_text_threshold:
                logger.warning(
                    f"Native extraction produced insufficient text ({len(full_text)} chars). Trying OCR..."
                )

                if use_ocr_fallback:
                    # Convert PDF pages to images and use OCR
                    pages_data, full_text = self._extract_with_ocr(doc)
                    extraction_method = "ocr"
                else:
                    logger.warning("OCR fallback disabled. Returning sparse text.")
                    extraction_method = "native_sparse"
            else:
                logger.info(
                    f"Native extraction successful. Extracted {len(full_text)} characters."
                )
                extraction_method = "native"

            doc.close()

            return {
                "text": full_text,
                "pages": pages_data,
                "metadata": metadata,
                "extraction_method": extraction_method,
                "total_pages": total_pages,
            }

        except Exception as e:
            logger.error(f"PDF extraction failed: {e}", exc_info=True)
            raise Exception(f"Failed to extract text from PDF: {str(e)}")

    def _extract_metadata(self, doc: fitz.Document) -> Dict[str, str]:
        """Extract PDF metadata."""
        metadata = doc.metadata
        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "creator": metadata.get("creator", ""),
            "producer": metadata.get("producer", ""),
            "creation_date": metadata.get("creationDate", ""),
            "modification_date": metadata.get("modDate", ""),
        }

    def _extract_native(
        self, doc: fitz.Document
    ) -> Tuple[List[Dict[str, any]], str]:
        """
        Extract text using PyMuPDF's native extraction.

        Returns:
            Tuple of (pages_data, full_text)
        """
        pages_data = []
        full_text_parts = []

        for page_num in range(len(doc)):
            page = doc[page_num]

            # Extract text with layout preservation
            text = page.get_text("text")

            # Extract tables (basic detection)
            tables = self._detect_tables(page)

            page_data = {
                "page_number": page_num + 1,
                "text": text,
                "char_count": len(text),
                "has_tables": len(tables) > 0,
                "table_count": len(tables),
            }

            pages_data.append(page_data)
            full_text_parts.append(f"--- Page {page_num + 1} ---\n{text}\n")

        full_text = "\n".join(full_text_parts)
        return pages_data, full_text

    def _detect_tables(self, page: fitz.Page) -> List[Dict]:
        """
        Detect tables in a page (basic implementation).

        Returns:
            List of detected tables with bounding boxes
        """
        tables = []

        # Simple table detection: look for grid-like structures
        # This is a placeholder - more sophisticated detection can be added
        drawings = page.get_drawings()

        # Group horizontal and vertical lines
        h_lines = []
        v_lines = []

        for drawing in drawings:
            for item in drawing["items"]:
                if item[0] == "l":  # Line
                    x0, y0, x1, y1 = item[1:5]
                    if abs(y1 - y0) < 2:  # Horizontal line
                        h_lines.append((x0, y0, x1, y1))
                    elif abs(x1 - x0) < 2:  # Vertical line
                        v_lines.append((x0, y0, x1, y1))

        # If we have both horizontal and vertical lines, likely a table
        if len(h_lines) >= 2 and len(v_lines) >= 2:
            tables.append(
                {
                    "horizontal_lines": len(h_lines),
                    "vertical_lines": len(v_lines),
                    "type": "grid",
                }
            )

        return tables

    def _extract_with_ocr(
        self, doc: fitz.Document
    ) -> Tuple[List[Dict[str, any]], str]:
        """
        Extract text using OCR (Surya or Google Vision).

        Returns:
            Tuple of (pages_data, full_text)
        """
        pages_data = []
        full_text_parts = []

        logger.info(f"Converting {len(doc)} pages to images for OCR...")

        for page_num in range(len(doc)):
            page = doc[page_num]

            # Render page to image (300 DPI for better OCR)
            pix = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72))

            # Convert to PIL Image
            img_data = pix.tobytes("png")
            img = Image.open(img_data)

            # Run OCR
            try:
                ocr_text = extract_text_with_ocr(img)

                page_data = {
                    "page_number": page_num + 1,
                    "text": ocr_text,
                    "char_count": len(ocr_text),
                    "extraction_method": "ocr",
                }

                pages_data.append(page_data)
                full_text_parts.append(f"--- Page {page_num + 1} ---\n{ocr_text}\n")

                logger.info(
                    f"OCR completed for page {page_num + 1}: {len(ocr_text)} characters"
                )

            except Exception as e:
                logger.error(f"OCR failed for page {page_num + 1}: {e}")
                pages_data.append(
                    {
                        "page_number": page_num + 1,
                        "text": "",
                        "char_count": 0,
                        "extraction_method": "ocr_failed",
                        "error": str(e),
                    }
                )

        full_text = "\n".join(full_text_parts)
        return pages_data, full_text

    def extract_page_range(
        self, pdf_bytes: bytes, start_page: int, end_page: int
    ) -> str:
        """
        Extract text from a specific page range.

        Args:
            pdf_bytes: PDF file content as bytes
            start_page: Starting page number (1-indexed)
            end_page: Ending page number (1-indexed, inclusive)

        Returns:
            Extracted text from specified pages
        """
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")

            # Validate page range
            if start_page < 1 or end_page > len(doc):
                raise ValueError(
                    f"Invalid page range: {start_page}-{end_page} (total pages: {len(doc)})"
                )

            text_parts = []
            for page_num in range(start_page - 1, end_page):
                page = doc[page_num]
                text = page.get_text("text")
                text_parts.append(f"--- Page {page_num + 1} ---\n{text}\n")

            doc.close()
            return "\n".join(text_parts)

        except Exception as e:
            logger.error(f"Failed to extract page range {start_page}-{end_page}: {e}")
            raise


# Singleton instance
pdf_extractor = PDFExtractor()
