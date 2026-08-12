"""Paper CRUD and management."""
from typing import List, Optional
from datetime import datetime
from app.database import get_session
from app.database.models import Paper, Project
from app.utils import deduplicate_papers, generate_id

class PaperManager:
    def __init__(self):
        self.session = get_session()
    
    def add_paper(self, project_id: str, paper_data: dict) -> Optional[Paper]:
        """Add a paper to a project."""
        
        # Check for duplicates
        if paper_data.get("doi"):
            existing = self.session.query(Paper).filter(
                Paper.project_id == project_id,
                Paper.doi == paper_data["doi"]
            ).first()
            if existing:
                return existing  # Already exists
        
        if paper_data.get("pmid"):
            existing = self.session.query(Paper).filter(
                Paper.project_id == project_id,
                Paper.pmid == paper_data["pmid"]
            ).first()
            if existing:
                return existing
        
        # Check title similarity
        title = paper_data.get("title", "")
        if title:
            existing = self.session.query(Paper).filter(
                Paper.project_id == project_id,
                Paper.title == title
            ).first()
            if existing:
                return existing
        
        paper = Paper(
            project_id=project_id,
            title=paper_data.get("title", "Unknown"),
            authors=paper_data.get("authors", ""),
            abstract=paper_data.get("abstract", ""),
            journal=paper_data.get("journal", ""),
            year=paper_data.get("year", ""),
            doi=paper_data.get("doi", ""),
            pmid=paper_data.get("pmid", ""),
            pmcid=paper_data.get("pmcid", ""),
            url=paper_data.get("url", ""),
            pdf_url=paper_data.get("pdf_url", ""),
            source=paper_data.get("source", ""),
            tags=paper_data.get("tags", []),
        )
        
        self.session.add(paper)
        self.session.commit()
        return paper
    
    def add_papers_batch(self, project_id: str, papers_data: List[dict]) -> int:
        """Add multiple papers. Returns count of newly added."""
        added = 0
        for paper_data in papers_data:
            paper = self.add_paper(project_id, paper_data)
            if paper:
                added += 1
        return added
    
    def get_paper(self, paper_id: str) -> Optional[Paper]:
        return self.session.query(Paper).filter(Paper.id == paper_id).first()
    
    def get_project_papers(self, project_id: str, filters: dict = None) -> List[Paper]:
        query = self.session.query(Paper).filter(Paper.project_id == project_id)
        
        if filters:
            if "read_status" in filters:
                query = query.filter(Paper.read_status == filters["read_status"])
            if "screening_status" in filters:
                query = query.filter(Paper.screening_status == filters["screening_status"])
            if "tag" in filters:
                query = query.filter(Paper.tags.contains([filters["tag"]]))
            if "source" in filters:
                query = query.filter(Paper.source == filters["source"])
            if "year_from" in filters:
                query = query.filter(Paper.year >= filters["year_from"])
            if "search" in filters:
                query = query.filter(
                    Paper.title.ilike(f"%{filters['search']}%") |
                    Paper.authors.ilike(f"%{filters['search']}%")
                )
        
        return query.order_by(Paper.added_at.desc()).all()
    
    def update_paper(self, paper_id: str, **kwargs) -> Optional[Paper]:
        paper = self.get_paper(paper_id)
        if paper:
            for key, value in kwargs.items():
                if hasattr(paper, key):
                    setattr(paper, key, value)
            self.session.commit()
        return paper
    
    def mark_read_status(self, paper_id: str, status: str):
        """Mark paper as unread, reading, or read."""
        valid = ["unread", "reading", "read"]
        if status in valid:
            return self.update_paper(paper_id, read_status=status)
    
    def mark_importance(self, paper_id: str, level: str):
        """Mark paper importance: important, review, critical."""
        return self.update_paper(paper_id, importance=level)
    
    def add_tag(self, paper_id: str, tag: str):
        paper = self.get_paper(paper_id)
        if paper and tag not in (paper.tags or []):
            tags = list(paper.tags or [])
            tags.append(tag)
            return self.update_paper(paper_id, tags=tags)
    
    def remove_tag(self, paper_id: str, tag: str):
        paper = self.get_paper(paper_id)
        if paper and tag in (paper.tags or []):
            tags = list(paper.tags or [])
            tags.remove(tag)
            return self.update_paper(paper_id, tags=tags)
    
    def update_screening(self, paper_id: str, status: str, notes: str = ""):
        """Update screening decision."""
        valid = ["unscreened", "included", "excluded", "maybe"]
        if status in valid:
            return self.update_paper(
                paper_id,
                screening_status=status,
                screening_notes=notes
            )
    
    def move_to_project(self, paper_id: str, new_project_id: str):
        """Copy paper to another project."""
        paper = self.get_paper(paper_id)
        if paper:
            new_paper_data = {
                "title": paper.title,
                "authors": paper.authors,
                "abstract": paper.abstract,
                "journal": paper.journal,
                "year": paper.year,
                "doi": paper.doi,
                "pmid": paper.pmid,
                "pmcid": paper.pmcid,
                "url": paper.url,
                "pdf_url": paper.pdf_url,
                "source": paper.source,
                "tags": paper.tags,
            }
            return self.add_paper(new_project_id, new_paper_data)
    
    def delete_paper(self, paper_id: str) -> bool:
        paper = self.get_paper(paper_id)
        if paper:
            self.session.delete(paper)
            self.session.commit()
            return True
        return False
    
    def get_paper_stats(self, project_id: str) -> dict:
        """Get statistics about papers in a project."""
        papers = self.get_project_papers(project_id)
        total = len(papers)
        
        return {
            "total": total,
            "downloaded": len([p for p in papers if p.full_text_available]),
            "by_source": {s: len([p for p in papers if p.source == s]) for s in set(p.source for p in papers)},
            "by_status": {
                "unread": len([p for p in papers if p.read_status == "unread"]),
                "reading": len([p for p in papers if p.read_status == "reading"]),
                "read": len([p for p in papers if p.read_status == "read"]),
            },
            "by_screening": {
                "unscreened": len([p for p in papers if p.screening_status == "unscreened"]),
                "included": len([p for p in papers if p.screening_status == "included"]),
                "excluded": len([p for p in papers if p.screening_status == "excluded"]),
                "maybe": len([p for p in papers if p.screening_status == "maybe"]),
            },
            "by_year": {},
            "all_tags": list(set(tag for p in papers for tag in (p.tags or []))),
        }
    
    def close(self):
        self.session.close()