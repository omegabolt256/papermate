"""Systematic review workflow manager."""
from typing import List, Dict, Optional
from datetime import datetime
from app.database import get_session
from app.database.models import Paper, ScreeningDecision, Project

class SystematicReviewWorkflow:
    """Manage systematic review workflow steps."""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.session = get_session()
    
    def get_status(self) -> Dict:
        """Get current systematic review status."""
        papers = self.session.query(Paper).filter(
            Paper.project_id == self.project_id
        ).all()
        
        total = len(papers)
        screened = sum(1 for p in papers if p.screening_status != "unscreened")
        included = sum(1 for p in papers if p.screening_status == "included")
        excluded = sum(1 for p in papers if p.screening_status == "excluded")
        maybe = sum(1 for p in papers if p.screening_status == "maybe")
        
        return {
            "total_identified": total,
            "screened": screened,
            "remaining": total - screened,
            "included": included,
            "excluded": excluded,
            "maybe": maybe,
            "completion_pct": round((screened / total * 100) if total > 0 else 0, 1),
        }
    
    def screen_paper(self, paper_id: str, decision: str, reason: str = "",
                     ai_suggestion: str = "", ai_confidence: float = 0.0,
                     user_override: bool = True) -> bool:
        """Record a screening decision."""
        valid = ["include", "exclude", "maybe"]
        if decision not in valid:
            return False
        
        # Update paper
        paper = self.session.query(Paper).filter(Paper.id == paper_id).first()
        if paper:
            paper.screening_status = decision
            paper.screening_notes = reason
        
        # Record decision
        sd = ScreeningDecision(
            project_id=self.project_id,
            paper_id=paper_id,
            decision=decision,
            reason=reason,
            ai_suggestion=ai_suggestion,
            ai_confidence=ai_confidence,
            user_override=user_override,
            screening_round=1,
        )
        self.session.add(sd)
        self.session.commit()
        return True
    
    def get_next_unscreened(self) -> Optional[Dict]:
        """Get next paper to screen."""
        paper = self.session.query(Paper).filter(
            Paper.project_id == self.project_id,
            Paper.screening_status == "unscreened"
        ).first()
        
        if paper:
            return {
                "id": paper.id,
                "title": paper.title,
                "authors": paper.authors,
                "year": paper.year,
                "abstract": paper.abstract[:300] if paper.abstract else "",
                "source": paper.source,
            }
        return None
    
    def get_screening_history(self, limit: int = 50) -> List[Dict]:
        """Get screening history."""
        decisions = self.session.query(ScreeningDecision).filter(
            ScreeningDecision.project_id == self.project_id
        ).order_by(ScreeningDecision.timestamp.desc()).limit(limit).all()
        
        return [
            {
                "paper_id": d.paper_id,
                "decision": d.decision,
                "reason": d.reason,
                "ai_suggestion": d.ai_suggestion,
                "timestamp": d.timestamp.isoformat() if d.timestamp else None,
            }
            for d in decisions
        ]
    
    def get_included_papers(self) -> List[Dict]:
        """Get all included papers."""
        papers = self.session.query(Paper).filter(
            Paper.project_id == self.project_id,
            Paper.screening_status == "included"
        ).all()
        
        return [
            {"id": p.id, "title": p.title, "authors": p.authors, "year": p.year}
            for p in papers
        ]
    
    def get_excluded_papers(self) -> List[Dict]:
        """Get excluded papers with reasons."""
        papers = self.session.query(Paper).filter(
            Paper.project_id == self.project_id,
            Paper.screening_status == "excluded"
        ).all()
        
        return [
            {
                "id": p.id, "title": p.title,
                "reason": p.screening_notes or "No reason recorded"
            }
            for p in papers
        ]
    
    def close(self):
        self.session.close()