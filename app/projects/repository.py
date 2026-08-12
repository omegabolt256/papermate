"""Database operations for projects."""
from typing import List, Optional
from datetime import datetime
from app.database import get_session
from app.database.models import Project, Paper, Chat, Message, Search, Note, Evidence, ScreeningDecision

class ProjectRepository:
    def __init__(self):
        self.session = get_session()
    
    def create(self, name: str, description: str = "") -> Project:
        # Find highest serial number
        highest = self.session.query(Project).order_by(Project.serial_number.desc()).first()
        next_serial = (highest.serial_number + 1) if highest and highest.serial_number else 1
        
        project = Project(
            serial_number=next_serial,
            name=name, 
            description=description
        )
        self.session.add(project)
        self.session.commit()
        return project
    
    def get(self, project_id: str) -> Optional[Project]:
        return self.session.query(Project).filter(Project.id == project_id).first()
    
    def get_all(self, status: str = None) -> List[Project]:
        query = self.session.query(Project)
        if status:
            query = query.filter(Project.status == status)
        return query.order_by(Project.last_opened_at.desc()).all()
    
    def get_recent(self, limit: int = 5) -> List[Project]:
        return self.session.query(Project)\
            .filter(Project.status == "active")\
            .order_by(Project.last_opened_at.desc())\
            .limit(limit).all()
    
    def update(self, project_id: str, **kwargs) -> Optional[Project]:
        project = self.get(project_id)
        if project:
            for key, value in kwargs.items():
                if hasattr(project, key):
                    setattr(project, key, value)
            project.updated_at = datetime.utcnow()
            self.session.commit()
        return project
    
    def touch(self, project_id: str):
        """Update last_opened_at timestamp."""
        project = self.get(project_id)
        if project:
            project.last_opened_at = datetime.utcnow()
            self.session.commit()
    
    def delete(self, project_id: str) -> bool:
        project = self.get(project_id)
        if project:
            self.session.delete(project)
            self.session.commit()
            return True
        return False
    
    def archive(self, project_id: str) -> Optional[Project]:
        return self.update(project_id, status="archived")
    
    def get_stats(self, project_id: str) -> dict:
        project = self.get(project_id)
        if not project:
            return {}
        return {
            "paper_count": len(project.papers),
            "downloaded_count": len([p for p in project.papers if p.full_text_available]),
            "chat_count": len(project.chats),
            "search_count": len(project.searches),
            "screened_count": len([p for p in project.papers if p.screening_status != "unscreened"]),
            "included_count": len([p for p in project.papers if p.screening_status == "included"]),
            "note_count": len(project.notes),
        }
    
    def search_by_name(self, query: str) -> List[Project]:
        return self.session.query(Project)\
            .filter(Project.name.ilike(f"%{query}%"))\
            .order_by(Project.last_opened_at.desc()).all()
    
    def close(self):
        self.session.close()