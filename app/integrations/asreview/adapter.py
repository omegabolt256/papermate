"""ASReview integration adapter."""
import os
import csv
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class ScreeningRecord:
    """A paper screening record for ASReview."""
    title: str
    abstract: str = ""
    authors: str = ""
    year: str = ""
    doi: str = ""
    pmid: str = ""
    keywords: str = ""
    included: Optional[int] = None  # 0=excluded, 1=included, None=unscreened
    screening_notes: str = ""

class ASReviewAdapter:
    """
    Adapter for ASReview systematic review tool.
    
    ASReview GitHub: https://github.com/asreview/asreview
    Install: pip install asreview
    
    Workflow:
    1. Export papers from project to ASReview format
    2. User runs ASReview screening (asreview simulate / asreview lab)
    3. Import screening results back into project
    """
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir) / "asreview"
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def is_installed(self) -> bool:
        """Check if ASReview is installed."""
        try:
            result = subprocess.run(
                ["asreview", "--version"],
                capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def export_for_screening(self, papers: List[Dict], output_file: str = None) -> str:
        """
        Export papers to ASReview-compatible CSV format.
        
        ASReview expects: title, abstract, keywords, authors, year, doi
        """
        if not output_file:
            output_file = str(self.data_dir / "papers_for_screening.csv")
        
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "title", "abstract", "keywords", "authors", "year", "doi", "pmid", "included"
            ])
            writer.writeheader()
            
            for paper in papers:
                writer.writerow({
                    "title": paper.get("title", ""),
                    "abstract": paper.get("abstract", ""),
                    "keywords": ", ".join(paper.get("tags", [])) if isinstance(paper.get("tags"), list) else paper.get("tags", ""),
                    "authors": paper.get("authors", ""),
                    "year": paper.get("year", ""),
                    "doi": paper.get("doi", ""),
                    "pmid": paper.get("pmid", ""),
                    "included": paper.get("screening_status", ""),
                })
        
        return output_file
    
    def import_screening_results(self, results_file: str) -> List[Dict]:
        """
        Import screening results from ASReview output.
        
        ASReview outputs CSV with columns: title, abstract, included, ...
        """
        results = []
        
        if not os.path.exists(results_file):
            return results
        
        with open(results_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                included_val = row.get("included", "")
                
                # Parse included status
                if str(included_val) in ["1", "1.0", "True", "true"]:
                    decision = "included"
                elif str(included_val) in ["0", "0.0", "False", "false"]:
                    decision = "excluded"
                else:
                    decision = "maybe"
                
                results.append({
                    "title": row.get("title", ""),
                    "doi": row.get("doi", ""),
                    "pmid": row.get("pmid", ""),
                    "decision": decision,
                    "screening_notes": row.get("notes", ""),
                })
        
        return results
    
    def create_project_file(self, papers: List[Dict]) -> str:
        """Create an ASReview project configuration."""
        config = {
            "name": "Medical Research Agent Export",
            "description": "Papers exported from Medical Research Agent",
            "paper_count": len(papers),
            "exported_at": str(__import__('datetime').datetime.now()),
            "papers": [
                {"title": p.get("title"), "doi": p.get("doi"), "pmid": p.get("pmid")}
                for p in papers[:100]
            ]
        }
        
        config_file = str(self.data_dir / "project_config.json")
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
        
        return config_file
    
    def get_screening_stats(self, results_file: str = None) -> Dict:
        """Get statistics from screening results."""
        if not results_file:
            results_file = str(self.data_dir / "screening_results.csv")
        
        if not os.path.exists(results_file):
            return {"error": "No results file found"}
        
        included = 0
        excluded = 0
        unscreened = 0
        
        with open(results_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                val = str(row.get("included", "")).strip()
                if val in ["1", "1.0", "True", "true"]:
                    included += 1
                elif val in ["0", "0.0", "False", "false"]:
                    excluded += 1
                else:
                    unscreened += 1
        
        return {
            "total": included + excluded + unscreened,
            "included": included,
            "excluded": excluded,
            "unscreened": unscreened,
        }