"""Paper file organization."""
import os
import re
import shutil
from pathlib import Path
from datetime import datetime

class PaperOrganizer:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        """Create standard directory structure."""
        for d in ["by_year", "by_source", "by_tag", "downloads"]:
            (self.base_dir / d).mkdir(parents=True, exist_ok=True)
    
    def organize_paper(self, paper, source_path: str = None) -> str:
        """
        Organize a paper file. Returns final path.
        If source_path is provided, copy from there.
        """
        title = getattr(paper, 'title', paper.get('title', 'paper'))
        year = getattr(paper, 'year', paper.get('year', ''))
        source = getattr(paper, 'source', paper.get('source', ''))
        
        # Create safe filename
        safe_title = re.sub(r'[^\w\s-]', '', str(title))[:60]
        safe_title = re.sub(r'\s+', '_', safe_title)
        filename = f"{safe_title}.pdf"
        
        # Organize by year
        if year:
            year_dir = self.base_dir / "by_year" / str(year)
            year_dir.mkdir(exist_ok=True)
            dest = year_dir / filename
        
        # Organize by source
        if source:
            source_dir = self.base_dir / "by_source" / re.sub(r'\s+', '_', str(source))
            source_dir.mkdir(exist_ok=True)
        
        # Copy file if source provided
        if source_path and os.path.exists(source_path):
            if dest and not dest.exists():
                shutil.copy2(source_path, dest)
            if source_path != str(dest):
                pass  # File already in place
        
        return str(dest) if dest else ""
    
    def get_organized_path(self, paper) -> str:
        """Get the expected organized path for a paper."""
        year = getattr(paper, 'year', paper.get('year', ''))
        title = getattr(paper, 'title', paper.get('title', 'paper'))
        safe_title = re.sub(r'[^\w\s-]', '', str(title))[:60]
        safe_title = re.sub(r'\s+', '_', safe_title)
        
        if year:
            return str(self.base_dir / "by_year" / str(year) / f"{safe_title}.pdf")
        return str(self.base_dir / "downloads" / f"{safe_title}.pdf")
    
    def list_organized_papers(self) -> list:
        """List all organized paper files."""
        papers = []
        by_year = self.base_dir / "by_year"
        if by_year.exists():
            for year_dir in by_year.iterdir():
                if year_dir.is_dir():
                    for pdf in year_dir.glob("*.pdf"):
                        papers.append({
                            "year": year_dir.name,
                            "filename": pdf.name,
                            "path": str(pdf),
                            "size": pdf.stat().st_size
                        })
        return papers
    
    def get_storage_stats(self) -> dict:
        """Get storage statistics."""
        total_size = 0
        total_files = 0
        by_year = {}
        
        year_dir = self.base_dir / "by_year"
        if year_dir.exists():
            for yd in year_dir.iterdir():
                if yd.is_dir():
                    files = list(yd.glob("*.pdf"))
                    size = sum(f.stat().st_size for f in files)
                    by_year[yd.name] = {"files": len(files), "size": size}
                    total_size += size
                    total_files += len(files)
        
        return {
            "total_files": total_files,
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024*1024), 2),
            "by_year": by_year
        }