"""
PDF Extractor Module

Handles extraction of text, tables, and metadata from PDF files
Includes automatic space restoration for malformed PDFs
"""

import re
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
    
    def __init__(self, pdf_path: Path, fix_spaces: bool = True):
        """
        Initialize PDF extractor
        
        Args:
            pdf_path: Path to PDF file
            fix_spaces: If True, attempts to restore missing spaces in extracted text
        """
        self.pdf_path = Path(pdf_path)
        self.fix_spaces = fix_spaces
        
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
                        # Fix missing spaces in extracted text if enabled
                        if self.fix_spaces:
                            lines = [self._fix_missing_spaces(line) for line in lines]
                        page_lines[i] = lines
                    else:
                        page_lines[i] = []
        except Exception as e:
            print(f"Warning: pdfplumber failed for {self.pdf_path.name}: {e}")
            # Fallback to pypdf
            page_lines = self._extract_with_pypdf()
            
        return page_lines
    
    def _fix_missing_spaces(self, text: str) -> str:
        """
        Fix missing spaces in extracted text
        
        Handles cases like:
        - "Motivated anddetail-oriented" -> "Motivated and detail-oriented"
        - "postgraduatewith" -> "postgraduate with"
        - "Chemistry postgraduate" (already correct, don't change)
        
        Args:
            text: Text with potential missing spaces
            
        Returns:
            Text with spaces restored where likely missing
        """
        import re
        
        # Pattern 1: Fix lowercase-to-uppercase transitions (camelCase)
        # "detailOriented" -> "detail Oriented"
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        
        # Pattern 2: Fix common word concatenations
        # Define common words that often get concatenated
        # Sort by length (longest first) to avoid partial replacements
        common_words = sorted([
            # Common connecting words
            'and', 'the', 'with', 'for', 'from', 'that', 'this', 'have', 'has',
            'are', 'were', 'was', 'been', 'will', 'can', 'could', 'would', 'should',
            'but', 'not', 'all', 'when', 'which', 'who', 'where',
            # Common descriptive words
            'detail', 'oriented', 'based', 'focused', 'driven', 'minded',
            'working', 'thinking', 'skills', 'experience', 'background',
            # Education/professional words
            'postgraduate', 'undergraduate', 'graduate', 'professional',
            'chemistry', 'physics', 'biology', 'science', 'engineering'
        ], key=len, reverse=True)
        
        # Fix concatenated common words
        # Pattern: word boundary + lowercase letter(s) + common word
        for word in common_words:
            # Look for patterns where a word is concatenated without space
            # Example: "anddetail" -> "and detail"
            
            # Before the word (something concatenated before it)
            pattern = r'([a-z])(' + re.escape(word) + r')(?=[\s\-.,;:]|$)'
            text = re.sub(pattern, r'\1 \2', text, flags=re.IGNORECASE)
            
            # After the word (word concatenated with something after)
            pattern = r'(?:^|[\s\-.,;:])(' + re.escape(word) + r')([a-z])'
            text = re.sub(pattern, r'\1 \2', text, flags=re.IGNORECASE)
        
        # Pattern 3: Fix specific problematic patterns we've seen
        # "anddetail-oriented" type issues
        fixes = {
            r'anddetail': 'and detail',
            r'withexperience': 'with experience',
            r'postgraduatewith': 'postgraduate with',
            r'chemistrypostgraduate': 'chemistry postgraduate'
        }
        
        for pattern, replacement in fixes.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _extract_with_pypdf(self) -> Dict[int, List[str]]:
        """Fallback extraction using pypdf"""
        page_lines = {}
        try:
            reader = PdfReader(self.pdf_path)
            for i, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if text:
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    # Fix missing spaces in extracted text if enabled
                    if self.fix_spaces:
                        lines = [self._fix_missing_spaces(line) for line in lines]
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
