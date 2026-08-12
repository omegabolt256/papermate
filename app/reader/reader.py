"""Built-in PDF reader with text extraction and navigation."""
import os
import re
import pymupdf as fitz
from pathlib import Path
from typing import List, Dict, Optional, Tuple

class PDFReader:
    """PDF reader with page navigation, search, and text extraction."""
    
    def __init__(self):
        self._doc = None
        self._current_page = 0
        self._filepath = None
    
    @property
    def is_open(self) -> bool:
        return self._doc is not None
    
    @property
    def filepath(self) -> str:
        return self._filepath
    
    @property
    def total_pages(self) -> int:
        return len(self._doc) if self._doc else 0
    
    @property
    def current_page(self) -> int:
        return self._current_page + 1  # 1-indexed for display
    
    def open(self, filepath: str) -> bool:
        """Open a PDF file."""
        if not os.path.exists(filepath):
            return False
        
        try:
            if self._doc:
                self.close()
            
            self._doc = fitz.open(filepath)
            self._filepath = filepath
            self._current_page = 0
            return True
        except Exception as e:
            return False
    
    def close(self):
        """Close the PDF."""
        if self._doc:
            self._doc.close()
            self._doc = None
            self._filepath = None
            self._current_page = 0
    
    def get_page(self, page_number: int = None) -> Optional[Dict]:
        """Get a specific page's content."""
        if not self._doc:
            return None
        
        if page_number is None:
            page_number = self._current_page
        
        # Convert to 0-indexed
        page_idx = page_number - 1 if page_number > 0 else 0
        
        if page_idx < 0 or page_idx >= len(self._doc):
            return None
        
        try:
            page = self._doc[page_idx]
            text = page.get_text()
            
            return {
                "page_number": page_number,
                "text": text.strip(),
                "char_count": len(text),
                "word_count": len(text.split()),
            }
        except:
            return None
    
    def next_page(self) -> Optional[Dict]:
        """Go to next page."""
        if self._doc and self._current_page < len(self._doc) - 1:
            self._current_page += 1
            return self.get_page()
        return None
    
    def prev_page(self) -> Optional[Dict]:
        """Go to previous page."""
        if self._doc and self._current_page > 0:
            self._current_page -= 1
            return self.get_page()
        return None
    
    def go_to_page(self, page_number: int) -> Optional[Dict]:
        """Go to a specific page."""
        if not self._doc:
            return None
        
        page_idx = page_number - 1
        if 0 <= page_idx < len(self._doc):
            self._current_page = page_idx
            return self.get_page()
        return None
    
    def search(self, query: str, max_results: int = 20) -> List[Dict]:
        """Search for text across all pages."""
        if not self._doc:
            return []
        
        results = []
        
        for page_num in range(len(self._doc)):
            if len(results) >= max_results:
                break
            
            page = self._doc[page_num]
            text = page.get_text()
            
            # Find all occurrences on this page
            query_lower = query.lower()
            text_lower = text.lower()
            
            start = 0
            while True:
                idx = text_lower.find(query_lower, start)
                if idx == -1:
                    break
                
                # Get context around the match
                context_start = max(0, idx - 50)
                context_end = min(len(text), idx + len(query) + 50)
                context = text[context_start:context_end].strip()
                
                results.append({
                    "page": page_num + 1,
                    "position": idx,
                    "context": f"...{context}...",
                    "exact_match": text[idx:idx + len(query)]
                })
                
                start = idx + 1
                
                if len(results) >= max_results:
                    break
        
        return results
    
    def get_section_text(self, page_number: int, start_pos: int, end_pos: int) -> str:
        """Get text between two positions on a page."""
        if not self._doc:
            return ""
        
        page_idx = page_number - 1
        if 0 <= page_idx < len(self._doc):
            text = self._doc[page_idx].get_text()
            return text[start_pos:end_pos].strip()
        return ""
    
       def highlight_text(self, page_number: int, start_pos: int, end_pos: int) -> Optional[str]:
        """Extract highlighted text from a page region."""
        return self.get_section_text(page_number, start_pos, end_pos)
    
    def get_text_around_position(self, page_number: int, position: int, context_chars: int = 500) -> Dict:
        """Get text and context around a position."""
        text = ""
        if self._doc:
            page_idx = page_number - 1
            if 0 <= page_idx < len(self._doc):
                text = self._doc[page_idx].get_text()
        
        start = max(0, position - context_chars)
        end = min(len(text), position + context_chars)
        
        return {
            "page": page_number,
            "selected": text[position:position+100] if position < len(text) else "",
            "before": text[start:position].strip(),
            "after": text[position:end].strip(),
            "full_context": text[start:end].strip(),
        }
    def get_metadata(self) -> Dict:
        """Get PDF metadata."""
        if not self._doc:
            return {}
        
        meta = self._doc.metadata
        return {
            "title": meta.get("title", ""),
            "author": meta.get("author", ""),
            "subject": meta.get("subject", ""),
            "creator": meta.get("creator", ""),
            "pages": len(self._doc),
            "file_size": os.path.getsize(self._filepath) if self._filepath else 0,
        }
    
    def extract_all_text(self) -> str:
        """Extract all text from PDF."""
        if not self._doc:
            return ""
        
        all_text = []
        for page_num in range(len(self._doc)):
            page = self._doc[page_num]
            all_text.append(page.get_text())
        
        return "\n\n".join(all_text)
    
    def get_pages_with_text(self, text_contains: str) -> List[int]:
        """Find pages containing specific text."""
        pages = []
        if not self._doc:
            return pages
        
        query = text_contains.lower()
        for page_num in range(len(self._doc)):
            text = self._doc[page_num].get_text().lower()
            if query in text:
                pages.append(page_num + 1)
        
        return pages
    
    def get_page_preview(self, page_number: int, max_chars: int = 500) -> str:
        """Get a preview of a page's content."""
        page = self.get_page(page_number)
        if page:
            text = page["text"]
            if len(text) > max_chars:
                return text[:max_chars] + "..."
            return text
        return ""