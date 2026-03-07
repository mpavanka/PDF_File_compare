"""
PDF Extractor Module

Handles extraction of text, tables, and metadata from PDF files
"""

from pathlib import Path
from typing import Dict, List, Any

try:
    from pypdf import PdfReader
    import pdfplumber
except ImportError:
    import subprocess
    import sys
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", 
                          "pypdf", "pdfplumber"])
    from pypdf import PdfReader
    import pdfplumber


class PDFExtractor:
    """Extract content from PDF files"""
    
    def __init__(self, pdf_path: Path):
        self.pdf_path = Path(pdf_path)
        
    def extract_text_lines(self) -> Dict[int, List[str]]:
        """
        Extract text from PDF as lines, organized by page
        
        Returns:
            Dict mapping page numbers to lists of text lines
        """
        page_lines = {}
        
        try:
            # Try pdfplumber first (better layout preservation)
            with pdfplumber.open(self.pdf_path) as pdf:
                for i, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        lines = [line.strip() for line in text.split('\n') if line.strip()]
                        page_lines[i] = lines
                    else:
                        page_lines[i] = []
        except Exception as e:
            print(f"Warning: pdfplumber failed for {self.pdf_path.name}: {e}")
            # Fallback to pypdf
            page_lines = self._extract_with_pypdf()
            
        return page_lines
    
    def _extract_with_pypdf(self) -> Dict[int, List[str]]:
        """Fallback extraction using pypdf"""
        page_lines = {}
        try:
            reader = PdfReader(self.pdf_path)
            for i, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if text:
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    page_lines[i] = lines
                else:
                    page_lines[i] = []
        except Exception as e:
            print(f"Error extracting text from {self.pdf_path.name}: {e}")
            page_lines = {}
        
        return page_lines
    
    def extract_tables(self) -> Dict[int, List]:
        """
        Extract tables from PDF, organized by page
        
        Returns:
            Dict mapping page numbers to lists of tables
        """
        page_tables = {}
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for i, page in enumerate(pdf.pages, 1):
                    tables = page.extract_tables()
                    page_tables[i] = tables if tables else []
        except Exception as e:
            print(f"Warning: Could not extract tables from {self.pdf_path.name}: {e}")
            page_tables = {}
            
        return page_tables
    
    def extract_metadata(self) -> Dict[str, Any]:
        """
        Extract PDF metadata
        
        Returns:
            Dict containing title, author, page count, etc.
        """
        try:
            reader = PdfReader(self.pdf_path)
            meta = reader.metadata
            
            return {
                'title': meta.title if meta and meta.title else 'N/A',
                'author': meta.author if meta and meta.author else 'N/A',
                'subject': meta.subject if meta and meta.subject else 'N/A',
                'creator': meta.creator if meta and meta.creator else 'N/A',
                'producer': meta.producer if meta and meta.producer else 'N/A',
                'creation_date': str(meta.creation_date) if meta and meta.creation_date else 'N/A',
                'modification_date': str(meta.modification_date) if meta and meta.modification_date else 'N/A',
                'page_count': len(reader.pages)
            }
        except Exception as e:
            print(f"Warning: Could not extract metadata from {self.pdf_path.name}: {e}")
            return {
                'title': 'N/A',
                'author': 'N/A',
                'page_count': 0
            }
    
    def get_page_count(self) -> int:
        """
        Get the number of pages in the PDF
        
        Returns:
            Number of pages
        """
        try:
            reader = PdfReader(self.pdf_path)
            return len(reader.pages)
        except Exception as e:
            print(f"Error getting page count from {self.pdf_path.name}: {e}")
            return 0
