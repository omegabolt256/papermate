"""PRISMA flow diagram data tracking."""
from typing import Dict, List
from datetime import datetime
from app.database import get_session
from app.database.models import Paper, Project
import json
import os
from pathlib import Path

class PrismaTracker:
    """Track PRISMA-style flow data for systematic reviews."""
    
    def __init__(self, project_id: str, data_dir: Path):
        self.project_id = project_id
        self.data_dir = Path(data_dir) / "prisma"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.session = get_session()
    
    def get_flow_data(self) -> Dict:
        """Get current PRISMA flow numbers."""
        papers = self.session.query(Paper).filter(
            Paper.project_id == self.project_id
        ).all()
        
        total = len(papers)
        excluded_titles = sum(1 for p in papers if p.screening_status == "excluded")
        excluded_full = 0  # User would set this
        included = sum(1 for p in papers if p.screening_status == "included")
        
        return {
            "records_identified": total,
            "records_after_duplicates": total,  # Dedup done at import
            "records_screened": sum(1 for p in papers if p.screening_status != "unscreened"),
            "records_excluded": excluded_titles,
            "full_text_assessed": included + excluded_full,
            "full_text_excluded": excluded_full,
            "studies_included": included,
            "last_updated": datetime.utcnow().isoformat(),
        }
    
    def update_flow(self, stage: str, count: int):
        """Update a specific PRISMA stage count."""
        flow_file = self.data_dir / "prisma_flow.json"
        
        data = {}
        if flow_file.exists():
            with open(flow_file, "r") as f:
                data = json.load(f)
        
        data[stage] = count
        data["last_updated"] = datetime.utcnow().isoformat()
        
        with open(flow_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def display_flow(self) -> str:
        """Generate PRISMA flow text display."""
        data = self.get_flow_data()
        
        flow = """
PRISMA 2020 FLOW DIAGRAM DATA
==============================

IDENTIFICATION
  Records identified:           {records_identified}
  
SCREENING
  Records after duplicates:     {records_after_duplicates}
  Records screened:             {records_screened}
  Records excluded:             {records_excluded}
  
ELIGIBILITY
  Full text assessed:           {full_text_assessed}
  Full text excluded:           {full_text_excluded}
  
INCLUDED
  Studies included:             {studies_included}
  
Last updated: {last_updated}
""".format(**data)
        
        return flow
    
    def export_prisma_csv(self, output_path: str = None) -> str:
        """Export PRISMA data as CSV."""
        if not output_path:
            output_path = str(self.data_dir / f"prisma_{datetime.now().strftime('%Y%m%d')}.csv")
        
        data = self.get_flow_data()
        
        with open(output_path, "w") as f:
            f.write("Stage,Count\n")
            for key, value in data.items():
                if key != "last_updated":
                    f.write(f"{key},{value}\n")
        
        return output_path
    
    def close(self):
        self.session.close()