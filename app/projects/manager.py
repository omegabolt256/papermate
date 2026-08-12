"""High-level project management with context."""
import os
import shutil
from typing import List, Optional
from datetime import datetime
from pathlib import Path
from config.settings import DATA_DIR
from .repository import ProjectRepository

class ProjectManager:
    def __init__(self):
        self.repo = ProjectRepository()
        self._active_project = None
        self._project_dir = DATA_DIR / "projects"
        self._project_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    def active_project(self):
        return self._active_project
    
    # ==================== PROJECT CRUD ====================
    
    def create_project(self, name: str, description: str = "", research_question: str = ""):
        project = self.repo.create(name=name, description=description)
        if research_question:
            self.repo.update(project.id, research_question=research_question)
        
        # Create project directory
        proj_dir = self._project_dir / project.id
        for subdir in ["papers", "downloads", "indexes", "exports", "reports", "metadata"]:
            (proj_dir / subdir).mkdir(parents=True, exist_ok=True)
        
        return project
    
    def open_project(self, project_id: str):
        project = self.repo.get(project_id)
        if project:
            self._active_project = project
            self.repo.touch(project_id)
        return project
    
    def close_project(self):
        self._active_project = None
    
    def get_all_projects(self, status: str = None):
        return self.repo.get_all(status=status)
    
    def get_recent_projects(self, limit: int = 5):
        return self.repo.get_recent(limit=limit)
    
    def search_projects(self, query: str):
        return self.repo.search_by_name(query)
    
    def rename_project(self, project_id: str, new_name: str):
        return self.repo.update(project_id, name=new_name)
    
    def archive_project(self, project_id: str):
        return self.repo.archive(project_id)
    
    def delete_project(self, project_id: str) -> bool:
        # Delete project files
        proj_dir = self._project_dir / project_id
        if proj_dir.exists():
            shutil.rmtree(proj_dir)
        
        # If deleting active project, close it
        if self._active_project and self._active_project.id == project_id:
            self._active_project = None
        
        return self.repo.delete(project_id)
    
    def get_project_stats(self, project_id: str = None):
        pid = project_id or (self._active_project.id if self._active_project else None)
        if not pid:
            return {}
        return self.repo.get_stats(pid)
    
    # ==================== PROJECT DIRECTORY ====================
    
    def get_project_dir(self, project_id: str = None) -> Path:
        pid = project_id or (self._active_project.id if self._active_project else None)
        if pid:
            return self._project_dir / pid
        return self._project_dir
    
    def get_papers_dir(self, project_id: str = None) -> Path:
        return self.get_project_dir(project_id) / "papers"
    
    def get_downloads_dir(self, project_id: str = None) -> Path:
        return self.get_project_dir(project_id) / "downloads"