"""Export research data in multiple formats."""
import csv
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from app.database import get_session
from app.database.models import Paper, Project, Message, Evidence

class ResearchExporter:
    """Export research data in various formats."""
    
    def __init__(self, project_id: str, export_dir: Path):
        self.project_id = project_id
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)
        self.session = get_session()
    
    def export_papers_csv(self, filename: str = None) -> str:
        """Export papers as CSV."""
        if not filename:
            filename = f"papers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = self.export_dir / filename
        
        papers = self.session.query(Paper).filter(
            Paper.project_id == self.project_id
        ).all()
        
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Title", "Authors", "Year", "Journal", "DOI", "PMID",
                "Source", "Screening", "Tags", "Abstract"
            ])
            for p in papers:
                writer.writerow([
                    p.title, p.authors, p.year, p.journal,
                    p.doi, p.pmid, p.source, p.screening_status,
                    ", ".join(p.tags or []), p.abstract[:200] if p.abstract else ""
                ])
        
        return str(filepath)
    
    def export_papers_bibtex(self, filename: str = None) -> str:
        """Export papers as BibTeX."""
        if not filename:
            filename = f"references_{datetime.now().strftime('%Y%m%d')}.bib"
        filepath = self.export_dir / filename
        
        papers = self.session.query(Paper).filter(
            Paper.project_id == self.project_id
        ).all()
        
        with open(filepath, "w", encoding="utf-8") as f:
            for i, p in enumerate(papers):
                author_key = p.authors.split(",")[0].split()[-1] if p.authors else "unknown"
                key = f"{author_key}{p.year or '0000'}{i}"
                
                f.write(f"@article{{{key},\n")
                f.write(f"  title = {{{p.title}}},\n")
                f.write(f"  author = {{{p.authors}}},\n")
                f.write(f"  year = {{{p.year}}},\n")
                if p.journal:
                    f.write(f"  journal = {{{p.journal}}},\n")
                if p.doi:
                    f.write(f"  doi = {{{p.doi}}},\n")
                if p.pmid:
                    f.write(f"  pmid = {{{p.pmid}}},\n")
                if p.url:
                    f.write(f"  url = {{{p.url}}},\n")
                f.write("}\n\n")
        
        return str(filepath)
    
    def export_papers_ris(self, filename: str = None) -> str:
        """Export papers as RIS format."""
        if not filename:
            filename = f"references_{datetime.now().strftime('%Y%m%d')}.ris"
        filepath = self.export_dir / filename
        
        papers = self.session.query(Paper).filter(
            Paper.project_id == self.project_id
        ).all()
        
        with open(filepath, "w", encoding="utf-8") as f:
            for p in papers:
                f.write("TY  - JOUR\n")
                f.write(f"TI  - {p.title}\n")
                for author in (p.authors or "").split(",")[:5]:
                    f.write(f"AU  - {author.strip()}\n")
                f.write(f"PY  - {p.year}\n")
                if p.journal:
                    f.write(f"JO  - {p.journal}\n")
                if p.doi:
                    f.write(f"DO  - {p.doi}\n")
                if p.url:
                    f.write(f"UR  - {p.url}\n")
                f.write(f"N2  - {p.abstract[:300] if p.abstract else ''}\n")
                f.write("ER  - \n\n")
        
        return str(filepath)
    
    def export_evidence_csv(self, filename: str = None) -> str:
        """Export evidence table as CSV."""
        if not filename:
            filename = f"evidence_{datetime.now().strftime('%Y%m%d')}.csv"
        filepath = self.export_dir / filename
        
        evidence_records = self.session.query(Evidence).filter(
            Evidence.project_id == self.project_id
        ).all()
        
        # Group by paper
        paper_evidence = {}
        all_fields = set()
        
        for e in evidence_records:
            if e.paper_id not in paper_evidence:
                paper_evidence[e.paper_id] = {}
            paper_evidence[e.paper_id][e.field] = e.value
            all_fields.add(e.field)
        
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["Paper Title", "Authors", "Year"] + sorted(all_fields)
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            
            for paper_id, fields in paper_evidence.items():
                paper = self.session.query(Paper).filter(Paper.id == paper_id).first()
                row = {
                    "Paper Title": paper.title if paper else "",
                    "Authors": paper.authors if paper else "",
                    "Year": paper.year if paper else "",
                }
                row.update(fields)
                writer.writerow(row)
        
        return str(filepath)
    
    def export_chats_markdown(self, filename: str = None) -> str:
        """Export all chats as Markdown."""
        if not filename:
            filename = f"chats_{datetime.now().strftime('%Y%m%d')}.md"
        filepath = self.export_dir / filename
        
        from app.database.models import Chat
        chats = self.session.query(Chat).filter(
            Chat.project_id == self.project_id
        ).all()
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# Research Chats\n\n")
            f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            
            for chat in chats:
                f.write(f"## {chat.title}\n\n")
                f.write(f"Created: {chat.created_at.strftime('%Y-%m-%d') if chat.created_at else ''}\n\n")
                
                for msg in chat.messages:
                    role = "**User**" if msg.role == "user" else "**AI**"
                    f.write(f"{role}: {msg.content[:500]}\n\n")
                    if msg.sources:
                        f.write(f"> Sources: {len(msg.sources)} papers\n\n")
                
                f.write("---\n\n")
        
        return str(filepath)
    
    def export_project_summary(self, filename: str = None) -> str:
        """Export full project summary as JSON."""
        if not filename:
            filename = f"project_summary_{datetime.now().strftime('%Y%m%d')}.json"
        filepath = self.export_dir / filename
        
        project = self.session.query(Project).filter(Project.id == self.project_id).first()
        papers = self.session.query(Paper).filter(Paper.project_id == self.project_id).all()
        
        summary = {
            "project_name": project.name if project else "",
            "research_question": project.research_question if project else "",
            "exported_at": datetime.now().isoformat(),
            "papers": [],
            "stats": {
                "total_papers": len(papers),
                "included": sum(1 for p in papers if p.screening_status == "included"),
                "excluded": sum(1 for p in papers if p.screening_status == "excluded"),
            }
        }
        
        for p in papers:
            summary["papers"].append({
                "title": p.title,
                "authors": p.authors,
                "year": p.year,
                "doi": p.doi,
                "pmid": p.pmid,
                "screening": p.screening_status,
                "tags": p.tags,
            })
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def export_all(self) -> Dict[str, str]:
        """Export everything. Returns dict of format -> filepath."""
        results = {}
        results["papers_csv"] = self.export_papers_csv()
        results["papers_bibtex"] = self.export_papers_bibtex()
        results["papers_ris"] = self.export_papers_ris()
        results["evidence_csv"] = self.export_evidence_csv()
        results["chats_md"] = self.export_chats_markdown()
        results["summary_json"] = self.export_project_summary()
        return results
    
    def close(self):
        self.session.close()