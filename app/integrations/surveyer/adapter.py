"""Surveyer compatibility adapter."""
import csv
import json
import os
from pathlib import Path
from typing import List, Dict

class SurveyerAdapter:
    """
    Adapter for Surveyer literature review workflow.
    
    Provides:
    - Export papers in Surveyer-compatible format
    - Track PRISMA flow data
    - Citation chasing support
    """
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir) / "surveyer"
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def export_papers(self, papers: List[Dict], format: str = "csv") -> str:
        """Export papers for Surveyer."""
        if format == "csv":
            return self._export_csv(papers)
        elif format == "ris":
            return self._export_ris(papers)
        elif format == "bibtex":
            return self._export_bibtex(papers)
        return ""
    
    def _export_csv(self, papers: List[Dict]) -> str:
        filepath = str(self.data_dir / "papers_export.csv")
        fieldnames = ["title", "authors", "year", "journal", "doi", "pmid", "abstract", "source", "tags"]
        
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for paper in papers:
                writer.writerow(paper)
        
        return filepath
    
    def _export_ris(self, papers: List[Dict]) -> str:
        filepath = str(self.data_dir / "papers_export.ris")
        
        with open(filepath, "w", encoding="utf-8") as f:
            for paper in papers:
                f.write("TY  - JOUR\n")
                f.write(f"TI  - {paper.get('title', '')}\n")
                
                authors = paper.get("authors", "")
                for author in authors.split(",")[:5]:
                    f.write(f"AU  - {author.strip()}\n")
                
                f.write(f"PY  - {paper.get('year', '')}\n")
                f.write(f"JO  - {paper.get('journal', '')}\n")
                f.write(f"DO  - {paper.get('doi', '')}\n")
                f.write(f"UR  - {paper.get('url', '')}\n")
                f.write(f"N2  - {paper.get('abstract', '')[:200]}\n")
                f.write("ER  - \n\n")
        
        return filepath
    
    def _export_bibtex(self, papers: List[Dict]) -> str:
        filepath = str(self.data_dir / "papers_export.bib")
        
        with open(filepath, "w", encoding="utf-8") as f:
            for i, paper in enumerate(papers):
                author_key = paper.get("authors", "unknown").split(",")[0].split()[-1] if paper.get("authors") else "unknown"
                year_key = paper.get("year", "0000")
                key = f"{author_key}{year_key}{i}"
                
                f.write(f"@article{{{key},\n")
                f.write(f"  title = {{{paper.get('title', '')}}},\n")
                f.write(f"  author = {{{paper.get('authors', '')}}},\n")
                f.write(f"  year = {{{paper.get('year', '')}}},\n")
                f.write(f"  journal = {{{paper.get('journal', '')}}},\n")
                f.write(f"  doi = {{{paper.get('doi', '')}}},\n")
                f.write("}\n\n")
        
        return filepath
    
    def track_prisma_flow(self, project_stats: Dict) -> Dict:
        """Track PRISMA-style flow data."""
        return {
            "records_identified": project_stats.get("total_papers", 0),
            "duplicates_removed": project_stats.get("duplicates", 0),
            "records_screened": project_stats.get("screened", 0),
            "records_excluded": project_stats.get("excluded", 0),
            "full_text_assessed": project_stats.get("full_text", 0),
            "full_text_excluded": project_stats.get("ft_excluded", 0),
            "studies_included": project_stats.get("included", 0),
        }
    
    def save_prisma_data(self, prisma_data: Dict) -> str:
        """Save PRISMA flow data."""
        filepath = str(self.data_dir / "prisma_flow.json")
        with open(filepath, "w") as f:
            json.dump(prisma_data, f, indent=2)
        return filepath