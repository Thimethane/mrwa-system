import PyPDF2
from typing import Dict, Any, List
import logging
import io

logger = logging.getLogger(__name__)


class PDFParser:
    """Parse PDF documents and extract content"""
    
    def __init__(self):
        self.supported_versions = ["1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7"]
    
    def parse(self, file_data: bytes) -> Dict[str, Any]:
        """Parse PDF file and extract text, metadata, and structure"""
        try:
            pdf_file = io.BytesIO(file_data)
            reader = PyPDF2.PdfReader(pdf_file)
            
            metadata = self._extract_metadata(reader)
            text_content = self._extract_text(reader)
            structure = self._extract_structure(reader)
            
            result = {
                "success": True,
                "metadata": metadata,
                "text_content": text_content,
                "structure": structure,
                "num_pages": len(reader.pages),
                "file_size_bytes": len(file_data)
            }
            
            logger.info(f"Successfully parsed PDF: {metadata.get('title', 'Unknown')} ({len(reader.pages)} pages)")
            return result
            
        except Exception as e:
            logger.error(f"PDF parsing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def _extract_metadata(self, reader: PyPDF2.PdfReader) -> Dict[str, Any]:
        """Extract PDF metadata"""
        metadata = {}
        if reader.metadata:
            metadata = {
                "title": reader.metadata.get("/Title", ""),
                "author": reader.metadata.get("/Author", ""),
                "subject": reader.metadata.get("/Subject", ""),
                "creator": reader.metadata.get("/Creator", ""),
                "producer": reader.metadata.get("/Producer", ""),
            }
        return metadata
    
    def _extract_text(self, reader: PyPDF2.PdfReader) -> str:
        """Extract text from all pages"""
        text_parts = []
        for page_num, page in enumerate(reader.pages):
            try:
                text = page.extract_text()
                if text.strip():
                    text_parts.append(f"--- Page {page_num + 1} ---\n{text}\n")
            except Exception as e:
                logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                text_parts.append(f"--- Page {page_num + 1} ---\n[Text extraction failed]\n")
        return "\n".join(text_parts)
    
    def _extract_structure(self, reader: PyPDF2.PdfReader) -> Dict[str, Any]:
        """Extract document structure"""
        structure = {
            "sections": [],
            "page_sizes": [],
            "has_images": False,
            "has_forms": False
        }
        
        for page in reader.pages:
            if hasattr(page, 'mediabox'):
                width = float(page.mediabox.width)
                height = float(page.mediabox.height)
                structure["page_sizes"].append({"width": width, "height": height})
        
        return structure
