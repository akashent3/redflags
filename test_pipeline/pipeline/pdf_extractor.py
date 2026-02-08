"""PDF text extraction with PyMuPDF."""

import logging
from typing import Dict, List, Tuple

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Extract text content from PDF files."""

    def extract_from_bytes(self, pdf_bytes: bytes) -> Dict:
        """Extract text from PDF bytes. Returns pages data and full text."""
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            total_pages = len(doc)
            logger.info(f"Processing PDF with {total_pages} pages")

            metadata = self._extract_metadata(doc)
            pages_data, full_text = self._extract_native(doc)

            doc.close()

            return {
                "text": full_text,
                "pages": pages_data,
                "metadata": metadata,
                "total_pages": total_pages,
            }
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}", exc_info=True)
            raise

    def _extract_metadata(self, doc: fitz.Document) -> Dict[str, str]:
        metadata = doc.metadata
        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "creation_date": metadata.get("creationDate", ""),
        }

    def _extract_native(self, doc: fitz.Document) -> Tuple[List[Dict], str]:
        pages_data = []
        full_text_parts = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")

            page_data = {
                "page_number": page_num + 1,
                "text": text,
                "char_count": len(text),
            }
            pages_data.append(page_data)
            full_text_parts.append(f"--- Page {page_num + 1} ---\n{text}\n")

        full_text = "\n".join(full_text_parts)
        return pages_data, full_text

    def slice_pdf(self, pdf_bytes: bytes, page_numbers: List[int]) -> bytes:
        """Create a new PDF containing only the specified pages (1-indexed)."""
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        sliced = fitz.open()

        for page_num in sorted(set(page_numbers)):
            if 1 <= page_num <= len(doc):
                sliced.insert_pdf(doc, from_page=page_num - 1, to_page=page_num - 1)

        sliced_bytes = sliced.tobytes()
        sliced.close()
        doc.close()

        logger.info(f"Sliced PDF: {len(page_numbers)} pages from {len(doc)} total")
        return sliced_bytes


pdf_extractor = PDFExtractor()
