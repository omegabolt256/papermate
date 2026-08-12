"""Research gap analysis."""
from typing import List, Dict
from app.models import get_model_provider
from app.database import get_session
from app.database.models import Paper

class GapAnalyzer:
    """Identify research gaps from literature."""
    
    def __init__(self):
        self.model = get_model_provider("ollama")
        self.session = get_session()
    
    def analyze_gaps(self, paper_ids: List[str], topic: str = None) -> Dict:
        """Analyze research gaps based on papers."""
        papers = []
        for pid in paper_ids:
            paper = self.session.query(Paper).filter(Paper.id == pid).first()
            if paper:
                papers.append(paper)
        
        if not papers:
            return {"gaps": [], "message": "No papers to analyze"}
        
        # Build context
        context_parts = []
        for i, p in enumerate(papers[:10], 1):
            context_parts.append(
                f"[{i}] {p.title} ({p.year})\n"
                f"    {p.abstract[:250] if p.abstract else 'N/A'}"
            )
        context = "\n\n".join(context_parts)
        
        prompt = f"""Analyze these papers and identify research gaps.

TOPIC: {topic or 'General research area'}

PAPERS:
{context}

Identify:
1. WHAT HAS BEEN STUDIED (summary of existing evidence)
2. RESEARCH GAPS (what questions remain unanswered?)
3. METHODOLOGICAL GAPS (what methods haven't been used?)
4. POPULATION GAPS (who hasn't been studied?)
5. FUTURE DIRECTIONS (specific research questions to explore)
6. PRIORITY AREAS (most important gaps to address first)

Be specific. Cite paper numbers [1], [2].
Do not fabricate gaps - only identify what is genuinely missing.

ANALYSIS:"""
        
        try:
            response = self.model.generate(prompt, max_tokens=600)
            return self._parse_gaps(response, papers)
        except:
            return {"gaps": [], "raw": ""}
    
    def _parse_gaps(self, response: str, papers: List) -> Dict:
        """Parse gap analysis."""
        gaps = {
            "what_studied": "",
            "research_gaps": [],
            "methodological_gaps": [],
            "population_gaps": [],
            "future_directions": [],
            "priority_areas": [],
            "papers_analyzed": len(papers),
            "raw": response,
        }
        
        current = ""
        for line in response.split("\n"):
            line = line.strip()
            lower = line.lower()
            
            if "what has been studied" in lower:
                current = "studied"
            elif "research gaps" in lower or "knowledge gaps" in lower:
                current = "gaps"
            elif "methodological" in lower:
                current = "method"
            elif "population" in lower:
                current = "population"
            elif "future direction" in lower:
                current = "future"
            elif "priority" in lower:
                current = "priority"
            elif line.startswith("-") or line.startswith("*") or line.startswith("•"):
                item = line.lstrip("-*• ").strip()
                if current == "gaps":
                    gaps["research_gaps"].append(item)
                elif current == "method":
                    gaps["methodological_gaps"].append(item)
                elif current == "population":
                    gaps["population_gaps"].append(item)
                elif current == "future":
                    gaps["future_directions"].append(item)
                elif current == "priority":
                    gaps["priority_areas"].append(item)
            elif line:
                if current == "studied":
                    gaps["what_studied"] += line + " "
        
        return gaps
    
    def suggest_research_question(self, paper_ids: List[str], topic: str = None) -> List[str]:
        """Suggest specific research questions based on identified gaps."""
        gap_analysis = self.analyze_gaps(paper_ids, topic)
        
        suggestions = []
        for gap in gap_analysis.get("research_gaps", [])[:3]:
            suggestions.append(f"Investigate: {gap}")
        for direction in gap_analysis.get("future_directions", [])[:2]:
            suggestions.append(direction)
        
        return suggestions if suggestions else ["No specific suggestions generated."]
    
    def close(self):
        self.session.close()