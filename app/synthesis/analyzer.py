"""Evidence synthesis and grading."""
from typing import List, Dict, Optional
from app.models import get_model_provider
from app.database import get_session
from app.database.models import Paper
import json

class SynthesisAnalyzer:
    """Synthesize evidence across multiple papers."""
    
    def __init__(self):
        self.model = get_model_provider("ollama")
        self.session = get_session()
    
    def synthesize(self, paper_ids: List[str], question: str = None) -> Dict:
        """Synthesize evidence from multiple papers."""
        papers = []
        for pid in paper_ids:
            paper = self.session.query(Paper).filter(Paper.id == pid).first()
            if paper:
                papers.append(paper)
        
        if not papers:
            return {"error": "No papers found"}
        
        # Build context
        context_parts = []
        for i, p in enumerate(papers[:10], 1):
            context_parts.append(
                f"[{i}] {p.title}\n"
                f"Authors: {p.authors} ({p.year})\n"
                f"Abstract: {p.abstract[:400] if p.abstract else 'N/A'}"
            )
        context = "\n\n".join(context_parts)
        
        prompt = f"""You are a medical research analyst. Synthesize evidence from these papers.

PAPERS:
{context}

QUESTION: {question or 'What is the overall evidence from these studies?'}

Provide:
1. EVIDENCE SUMMARY (3-5 sentences)
2. EVIDENCE STRENGTH (High/Moderate/Low/Very Low with reasoning)
3. CONSISTENCY (Are findings consistent across studies?)
4. KEY FINDINGS (bullet points, cite paper numbers [1], [2])
5. LIMITATIONS (across all studies)
6. RECOMMENDATIONS (for future research)

RULES:
- Only use information from the papers above
- Cite sources as [1], [2], etc.
- Never fabricate findings

ANALYSIS:"""
        
        try:
            response = self.model.generate(prompt, max_tokens=800)
            return self._parse_synthesis(response, papers)
        except Exception as e:
            return {"error": str(e), "raw": ""}
    
    def _parse_synthesis(self, response: str, papers: List) -> Dict:
        """Parse synthesis response into structured data."""
        sections = {
            "evidence_summary": "",
            "evidence_strength": "",
            "consistency": "",
            "key_findings": [],
            "limitations": "",
            "recommendations": "",
            "papers_analyzed": len(papers),
            "sources": [
                {"number": i+1, "title": p.title, "authors": p.authors, "year": p.year}
                for i, p in enumerate(papers)
            ]
        }
        
        current_section = ""
        for line in response.split("\n"):
            line = line.strip()
            lower = line.lower()
            
            if "evidence summary" in lower:
                current_section = "summary"
            elif "evidence strength" in lower:
                current_section = "strength"
            elif "consistency" in lower:
                current_section = "consistency"
            elif "key findings" in lower:
                current_section = "findings"
            elif "limitations" in lower:
                current_section = "limitations"
            elif "recommendations" in lower:
                current_section = "recommendations"
            elif line.startswith("-") or line.startswith("*"):
                if current_section == "findings":
                    sections["key_findings"].append(line.lstrip("-* ").strip())
            elif line:
                if current_section == "summary":
                    sections["evidence_summary"] += line + " "
                elif current_section == "strength":
                    sections["evidence_strength"] += line + " "
                elif current_section == "consistency":
                    sections["consistency"] += line + " "
                elif current_section == "limitations":
                    sections["limitations"] += line + " "
                elif current_section == "recommendations":
                    sections["recommendations"] += line + " "
        
        return sections
    
    def grade_evidence(self, paper_ids: List[str]) -> List[Dict]:
        """Grade evidence quality for each paper."""
        grades = []
        
        for pid in paper_ids[:5]:
            paper = self.session.query(Paper).filter(Paper.id == pid).first()
            if not paper:
                continue
            
            prompt = f"""Grade the evidence quality of this study. Be transparent about reasoning.

PAPER: {paper.title}
Authors: {paper.authors} ({paper.year})
Abstract: {paper.abstract[:400] if paper.abstract else 'N/A'}

Assess:
1. Study design strength
2. Sample size adequacy  
3. Risk of bias
4. Precision of results
5. Overall evidence grade (High/Moderate/Low/Very Low)

Explain each rating.

GRADE:"""
            
            try:
                response = self.model.generate(prompt, max_tokens=300)
                
                # Extract overall grade
                grade = "Not rated"
                for g in ["High", "Moderate", "Low", "Very Low"]:
                    if g.lower() in response.lower():
                        grade = g
                        break
                
                grades.append({
                    "paper_id": pid,
                    "title": paper.title[:80],
                    "grade": grade,
                    "reasoning": response[:300],
                })
            except:
                pass
        
        return grades
    
    def close(self):
        self.session.close()