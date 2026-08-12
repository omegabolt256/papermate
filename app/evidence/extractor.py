"""Extract structured evidence from papers."""
from typing import List, Dict, Optional
from app.database import get_session
from app.database.models import Paper, Evidence
from app.models import get_model_provider
import json

class EvidenceExtractor:
    """Extract structured evidence from research papers."""
    
    def __init__(self):
        self.session = get_session()
        self.model = get_model_provider("ollama")
    
    def extract_from_paper(self, paper_id: str, fields: List[str] = None) -> Dict:
        """Extract evidence fields from a paper."""
        paper = self.session.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            return {}
        
        if fields is None:
            fields = [
                "study_design", "population", "sample_size",
                "intervention", "comparator", "outcome",
                "main_findings", "limitations", "funding"
            ]
        
        # Build prompt
        prompt = f"""Extract the following information from this research paper. 
Only use information explicitly stated in the paper. 
If information is not available, say "Not reported".

PAPER:
Title: {paper.title}
Authors: {paper.authors}
Year: {paper.year}
Abstract: {paper.abstract}

FIELDS TO EXTRACT:
{chr(10).join(f'- {f}' for f in fields)}

Provide output in JSON format:
{{"field_name": "extracted_value"}}

JSON:"""
        
        try:
            response = self.model.generate(prompt, max_tokens=500)
            
            # Try to parse JSON from response
            # Find JSON block
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                extracted = json.loads(json_str)
                
                # Save to database
                for field, value in extracted.items():
                    evidence = Evidence(
                        paper_id=paper_id,
                        project_id=paper.project_id,
                        category="extracted",
                        field=field,
                        value=str(value),
                        confidence=0.8,
                        source_type="ai_extracted"
                    )
                    self.session.add(evidence)
                
                self.session.commit()
                return extracted
        except:
            pass
        
        return {}
    
    def compare_papers(self, paper_ids: List[str], fields: List[str] = None) -> List[Dict]:
        """Compare evidence across multiple papers."""
        if fields is None:
            fields = [
                "study_design", "sample_size", "intervention",
                "main_findings", "limitations"
            ]
        
        results = []
        for pid in paper_ids:
            paper = self.session.query(Paper).filter(Paper.id == pid).first()
            if paper:
                evidence = self.extract_from_paper(pid, fields)
                evidence["_paper_title"] = paper.title
                evidence["_paper_authors"] = paper.authors
                evidence["_paper_year"] = paper.year
                results.append(evidence)
        
        return results
    
    def compare_papers_table(self, paper_ids: List[str], fields: List[str] = None) -> str:
        """Generate a comparison table."""
        if fields is None:
            fields = ["study_design", "sample_size", "intervention", "main_findings"]
        
        results = self.compare_papers(paper_ids, fields)
        
        if not results:
            return "No data to compare."
        
        # Build table
        table = "COMPARISON TABLE\n"
        table += "=" * 80 + "\n\n"
        
        for i, r in enumerate(results, 1):
            table += f"[{i}] {r.get('_paper_title', 'Unknown')[:70]}\n"
            table += f"    {r.get('_paper_authors', '')} ({r.get('_paper_year', '')})\n"
            table += "-" * 50 + "\n"
            
            for field in fields:
                value = r.get(field, "Not extracted")
                field_name = field.replace("_", " ").title()
                table += f"    {field_name}: {str(value)[:100]}\n"
            
            table += "\n"
        
        return table
    
    def get_evidence_for_paper(self, paper_id: str) -> List[Dict]:
        """Get all extracted evidence for a paper."""
        evidence = self.session.query(Evidence).filter(
            Evidence.paper_id == paper_id
        ).all()
        
        return [
            {
                "field": e.field,
                "value": e.value,
                "category": e.category,
                "confidence": e.confidence,
                "source_type": e.source_type,
            }
            for e in evidence
        ]
    
    def export_evidence_csv(self, project_id: str, output_path: str) -> str:
        """Export all evidence for a project as CSV."""
        import csv
        
        papers = self.session.query(Paper).filter(
            Paper.project_id == project_id
        ).all()
        
        all_fields = set()
        paper_data = {}
        
        for paper in papers:
            evidence_list = self.get_evidence_for_paper(paper.id)
            data = {"title": paper.title, "authors": paper.authors, "year": paper.year}
            
            for e in evidence_list:
                data[e["field"]] = e["value"]
                all_fields.add(e["field"])
            
            paper_data[paper.id] = data
        
        fieldnames = ["title", "authors", "year"] + sorted(all_fields)
        
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for data in paper_data.values():
                writer.writerow(data)
        
        return output_path
    
    def close(self):
        self.session.close()