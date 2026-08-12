"""Detect contradictions between studies."""
from typing import List, Dict
from app.models import get_model_provider
from app.database import get_session
from app.database.models import Paper

class ContradictionDetector:
    """Find contradictory findings across papers."""
    
    def __init__(self):
        self.model = get_model_provider("ollama")
        self.session = get_session()
    
    def detect_contradictions(self, paper_ids: List[str]) -> Dict:
        """Find contradictions between multiple papers."""
        papers = []
        for pid in paper_ids:
            paper = self.session.query(Paper).filter(Paper.id == pid).first()
            if paper:
                papers.append(paper)
        
        if len(papers) < 2:
            return {"contradictions": [], "message": "Need at least 2 papers to compare"}
        
        # Build paper summaries
        paper_summaries = []
        for i, p in enumerate(papers, 1):
            paper_summaries.append(
                f"[{i}] {p.title}\n"
                f"    Authors: {p.authors} ({p.year})\n"
                f"    Abstract: {p.abstract[:300] if p.abstract else 'N/A'}"
            )
        
        context = "\n\n".join(paper_summaries)
        
        prompt = f"""Compare these studies and identify any contradictions or conflicting findings.

STUDIES:
{context}

Identify:
1. CONFLICTING FINDINGS (what specifically disagrees?)
2. POSSIBLE REASONS for differences (methodology, population, dosage, etc.)
3. RESOLUTION (can the contradiction be resolved, or is more research needed?)

If no contradictions exist, say so clearly. Do not invent conflicts.

ANALYSIS:"""
        
        try:
            response = self.model.generate(prompt, max_tokens=500)
            return self._parse_contradictions(response, papers)
        except:
            return {"contradictions": [], "raw": ""}
    
    def _parse_contradictions(self, response: str, papers: List) -> Dict:
        """Parse contradiction analysis."""
        contradictions = []
        current = {}
        
        for line in response.split("\n"):
            line = line.strip()
            lower = line.lower()
            
            if "conflicting finding" in lower or "contradiction" in lower:
                if current:
                    contradictions.append(current)
                current = {"finding": line, "papers_involved": [], "reason": ""}
            elif "possible reason" in lower or "why" in lower:
                if current:
                    current["reason"] = line
            elif "resolution" in lower:
                if current:
                    current["resolution"] = line
        
        if current:
            contradictions.append(current)
        
        return {
            "contradictions": contradictions,
            "total_papers": len(papers),
            "papers": [
                {"number": i+1, "title": p.title[:60]} 
                for i, p in enumerate(papers)
            ],
            "raw_analysis": response,
        }
    
    def compare_findings(self, paper_id_1: str, paper_id_2: str) -> Dict:
        """Compare findings between two specific papers."""
        return self.detect_contradictions([paper_id_1, paper_id_2])
    
    def close(self):
        self.session.close()