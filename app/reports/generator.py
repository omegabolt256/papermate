"""Generate structured research reports."""
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from app.database import get_session
from app.database.models import Paper, Project
from app.models import get_model_provider
from app.synthesis import SynthesisAnalyzer, ContradictionDetector, GapAnalyzer
from app.review import PrismaTracker

class ReportGenerator:
    """Generate comprehensive research reports."""
    
    def __init__(self, project_id: str, data_dir: Path):
        self.project_id = project_id
        self.data_dir = Path(data_dir)
        self.reports_dir = self.data_dir / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.session = get_session()
        self.model = get_model_provider("ollama")
    
    def generate_full_report(self) -> str:
        """Generate a complete research report."""
        project = self.session.query(Project).filter(Project.id == self.project_id).first()
        if not project:
            return "Project not found."
        
        papers = self.session.query(Paper).filter(
            Paper.project_id == self.project_id
        ).all()
        
        included = [p for p in papers if p.screening_status == "included"]
        
        # Get synthesis data
        synthesizer = SynthesisAnalyzer()
        contradiction = ContradictionDetector()
        gaps = GapAnalyzer()
        prisma = PrismaTracker(self.project_id, self.data_dir)
        
        paper_ids = [p.id for p in (included or papers)[:10]]
        
        synthesis = synthesizer.synthesize(paper_ids, project.research_question)
        contradictions = contradiction.detect_contradictions(paper_ids)
        gap_analysis = gaps.analyze_gaps(paper_ids, project.research_question)
        prisma_data = prisma.get_flow_data()
        
        # Build report
        report = f"""
======================================================================
RESEARCH REPORT
======================================================================

TITLE: {project.name}
DATE: {datetime.now().strftime('%B %d, %Y')}

======================================================================
1. RESEARCH QUESTION
======================================================================

{project.research_question or 'Not specified'}

======================================================================
2. SEARCH STRATEGY
======================================================================

Databases searched: PubMed, Semantic Scholar, arXiv
Total papers identified: {len(papers)}
Papers included after screening: {len(included)}

======================================================================
3. PRISMA FLOW
======================================================================

Records identified:          {prisma_data.get('records_identified', 0)}
Records screened:            {prisma_data.get('records_screened', 0)}
Records excluded:            {prisma_data.get('records_excluded', 0)}
Studies included:            {prisma_data.get('studies_included', 0)}

======================================================================
4. EVIDENCE SYNTHESIS
======================================================================

{synthesis.get('evidence_summary', 'No synthesis available.')}

Evidence Strength: {synthesis.get('evidence_strength', 'Not assessed.')}

Key Findings:
"""
        for f in synthesis.get('key_findings', [])[:5]:
            report += f"  - {f}\n"
        
        report += f"""
======================================================================
5. CONTRADICTIONS
======================================================================
"""
        if contradictions.get('contradictions'):
            for c in contradictions['contradictions']:
                report += f"  - {c.get('finding', '')}\n"
        else:
            report += "  No significant contradictions detected.\n"
        
        report += f"""
======================================================================
6. RESEARCH GAPS
======================================================================
"""
        for g in gap_analysis.get('research_gaps', [])[:5]:
            report += f"  - {g}\n"
        
        report += f"""
======================================================================
7. LIMITATIONS
======================================================================

{synthesis.get('limitations', 'Not assessed.')}

======================================================================
8. CONCLUSIONS
======================================================================

{synthesis.get('recommendations', 'Not available.')}

======================================================================
9. REFERENCES
======================================================================
"""
        for i, p in enumerate((included or papers)[:10], 1):
            report += f"\n[{i}] {p.authors} ({p.year}). {p.title}."
            if p.journal:
                report += f" {p.journal}."
            if p.doi:
                report += f" DOI: {p.doi}"
        
        report += f"""

======================================================================
Generated by Medical Research Agent
{datetime.now().strftime('%Y-%m-%d %H:%M')}
======================================================================
"""
        
        # Clean up
        synthesizer.close()
        contradiction.close()
        gaps.close()
        prisma.close()
        
        return report
    
    def save_report(self, content: str, filename: str = None, format: str = "txt") -> str:
        """Save report to file."""
        if not filename:
            filename = f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if format == "md":
            filepath = self.reports_dir / f"{filename}.md"
        else:
            filepath = self.reports_dir / f"{filename}.txt"
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        return str(filepath)
    
    def generate_quick_summary(self) -> str:
        """Generate a quick one-page summary."""
        project = self.session.query(Project).filter(Project.id == self.project_id).first()
        papers = self.session.query(Paper).filter(Paper.project_id == self.project_id).all()
        
        included = [p for p in papers if p.screening_status == "included"]
        
        summary = f"""
QUICK RESEARCH SUMMARY
=======================
Project: {project.name if project else ''}
Question: {project.research_question if project else ''}
Papers: {len(papers)} total, {len(included)} included

Included Studies:
"""
        for i, p in enumerate(included[:5], 1):
            summary += f"  [{i}] {p.authors} ({p.year}) - {p.title[:80]}\n"
        
        return summary
    
    def close(self):
        self.session.close()