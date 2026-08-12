"""Citation navigation - link citations to actual paper content."""
import re
from typing import List, Dict, Optional, Tuple
from app.database import get_session
from app.database.models import Paper, Message

class CitationLinker:
    """Handles linking citations in AI responses to actual papers."""
    
    def __init__(self):
        self.session = get_session()
    
    def parse_citations(self, text: str) -> List[Dict]:
        """
        Parse citation references from text.
        Finds patterns like [1], [2], [1, p.7], [1,2,3]
        """
        citations = []
        
        # Pattern: [1], [2], [1,2,3], [1-3]
        pattern = r'\[(\d+(?:[-,]\d+)*)\]'
        matches = re.finditer(pattern, text)
        
        for match in matches:
            citation_text = match.group(1)
            position = match.start()
            
            # Parse individual numbers
            numbers = self._parse_citation_numbers(citation_text)
            
            citations.append({
                "original": match.group(0),
                "numbers": numbers,
                "position": position,
                "text": match.group(0),
            })
        
        # Also find page-specific citations: [1, p.7]
        page_pattern = r'\[(\d+),\s*p\.\s*(\d+)\]'
        page_matches = re.finditer(page_pattern, text)
        
        for match in page_matches:
            citations.append({
                "original": match.group(0),
                "numbers": [int(match.group(1))],
                "page": int(match.group(2)),
                "position": match.start(),
                "text": match.group(0),
            })
        
        return citations
    
    def _parse_citation_numbers(self, text: str) -> List[int]:
        """Parse citation numbers like '1,2,3' or '1-3'."""
        numbers = []
        parts = text.split(",")
        
        for part in parts:
            part = part.strip()
            if "-" in part:
                try:
                    start, end = part.split("-")
                    numbers.extend(range(int(start), int(end) + 1))
                except:
                    if part.isdigit():
                        numbers.append(int(part))
            elif part.isdigit():
                numbers.append(int(part))
        
        return numbers
    
    def link_citations_to_papers(self, citations: List[Dict], message_id: str) -> List[Dict]:
        """
        Link parsed citations to actual paper records.
        Uses sources stored with the message.
        """
        # Get the message to find attached sources
        message = self.session.query(Message).filter(Message.id == message_id).first()
        
        if not message or not message.sources:
            return citations
        
        sources = message.sources  # List of {paper_id, title, page, quote}
        
        linked = []
        for citation in citations:
            linked_citation = {**citation}
            linked_papers = []
            
            for num in citation.get("numbers", []):
                # Source indices are 0-based, citation numbers are 1-based
                source_idx = num - 1
                if 0 <= source_idx < len(sources):
                    source = sources[source_idx]
                    
                    # Get full paper details
                    paper = self.session.query(Paper).filter(
                        Paper.id == source.get("paper_id", "")
                    ).first()
                    
                    if paper:
                        linked_papers.append({
                            "paper_id": paper.id,
                            "title": paper.title,
                            "authors": paper.authors,
                            "year": paper.year,
                            "page": source.get("page", paper.pdf_path and "N/A" or "N/A"),
                            "quote": source.get("quote", ""),
                            "doi": paper.doi,
                            "pmid": paper.pmid,
                            "pdf_path": paper.pdf_path,
                        })
            
            linked_citation["papers"] = linked_papers
            linked.append(linked_citation)
        
        return linked
    
    def get_paper_for_citation(self, citation_number: int, message_id: str) -> Optional[Dict]:
        """Get the paper details for a specific citation number."""
        message = self.session.query(Message).filter(Message.id == message_id).first()
        
        if not message or not message.sources:
            return None
        
        idx = citation_number - 1
        if 0 <= idx < len(message.sources):
            source = message.sources[idx]
            paper = self.session.query(Paper).filter(
                Paper.id == source.get("paper_id", "")
            ).first()
            
            if paper:
                return {
                    "paper_id": paper.id,
                    "title": paper.title,
                    "authors": paper.authors,
                    "year": paper.year,
                    "doi": paper.doi,
                    "pmid": paper.pmid,
                    "pdf_path": paper.pdf_path,
                    "page": source.get("page", ""),
                    "quote": source.get("quote", ""),
                }
        
        return None
    
    def format_citation_text(self, citation: Dict) -> str:
        """Format a citation for display."""
        papers = citation.get("papers", [])
        if not papers:
            return citation.get("text", "")
        
        parts = []
        for p in papers:
            author_short = p["authors"].split(",")[0].split()[-1] if p["authors"] else "Unknown"
            parts.append(f"{author_short} et al. ({p['year']})")
        
        return ", ".join(parts)
    
    def close(self):
        self.session.close()