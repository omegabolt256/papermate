"""Watch folder - auto import PDFs dropped into a folder."""
import os
import time
from pathlib import Path
from datetime import datetime
from app.database import get_session
from app.database.models import Paper
import fitz
import re
import json

class FolderWatcher:
    """Watch a folder for new PDFs and auto-add them to a project."""
    
    def __init__(self, project_id: str, watch_dir: Path):
        self.project_id = project_id
        self.watch_dir = Path(watch_dir)
        self.watch_dir.mkdir(parents=True, exist_ok=True)
        self.processed_file = self.watch_dir / "processed.json"
        self.session = get_session()
        self._load_processed()
    
    def _load_processed(self):
        """Load list of already processed files."""
        if self.processed_file.exists():
            with open(self.processed_file, "r") as f:
                self.processed = set(json.load(f))
        else:
            self.processed = set()
    
    def _save_processed(self):
        with open(self.processed_file, "w") as f:
            json.dump(list(self.processed), f)
    
    def scan(self) -> list:
        """Scan for new PDFs and add them. Returns list of added papers."""
        added = []
        
        for pdf_file in self.watch_dir.glob("*.pdf"):
            if str(pdf_file) in self.processed:
                continue
            
            try:
                paper = self._import_pdf(pdf_file)
                if paper:
                    added.append(paper)
                    # Move to organized folder
                    year_dir = self.watch_dir / "imported" / (paper.year or "unknown")
                    year_dir.mkdir(parents=True, exist_ok=True)
                    dest = year_dir / pdf_file.name
                    pdf_file.rename(dest)
                    print(f"  [OK] Imported: {paper.title[:60]}")
            except Exception as e:
                print(f"  [SKIP] {pdf_file.name}: {e}")
            
            self.processed.add(str(pdf_file))
        
        self._save_processed()
        return added
    
    def _import_pdf(self, pdf_path: Path) -> Paper:
        """Extract metadata from PDF and create paper record."""
        doc = fitz.open(str(pdf_path))
        meta = doc.metadata
        
        title = meta.get("title", pdf_path.stem)
        authors = meta.get("author", "Unknown")
        
        year = "Unknown"
        date_str = meta.get("creationDate", "")
        match = re.search(r'(\d{4})', date_str)
        if match:
            year = match.group(1)
        
        # Check for duplicates
        existing = self.session.query(Paper).filter(
            Paper.project_id == self.project_id,
            Paper.title == title
        ).first()
        
        if existing:
            doc.close()
            return existing
        
        paper = Paper(
            project_id=self.project_id,
            title=title,
            authors=authors,
            year=year,
            pdf_path=str(pdf_path),
            full_text_available=True,
            source="Watch Folder",
            added_at=datetime.utcnow(),
        )
        
        self.session.add(paper)
        self.session.commit()
        doc.close()
        return paper
    
    def close(self):
        self.session.close()