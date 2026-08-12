"""Semantic Scholar search adapter."""
import requests
import time
from typing import List
from .base import LiteratureSource, PaperResult
from config.settings import SEMANTIC_SCHOLAR_API_KEY

class SemanticScholarAdapter(LiteratureSource):
    def get_source_name(self) -> str:
        return "Semantic Scholar"
    
    def search(self, query: str, max_results: int = 20, **filters) -> List[PaperResult]:
        papers = []
        time.sleep(1)
        
        try:
            url = "https://api.semanticscholar.org/graph/v1/paper/search"
            params = {
                "query": query,
                "limit": max_results,
                "fields": "title,authors,year,abstract,externalIds,openAccessPdf,url,journal,citationCount"
            }
            headers = {}
            if SEMANTIC_SCHOLAR_API_KEY:
                headers["x-api-key"] = SEMANTIC_SCHOLAR_API_KEY
            
            response = requests.get(url, params=params, headers=headers, timeout=15)
            data = response.json()
            
            for paper in data.get("data", []):
                authors = [a.get("name", a.get("authorName", "")) for a in paper.get("authors", [])]
                authors_str = ", ".join(authors[:4])
                if len(authors) > 4:
                    authors_str += " et al."
                
                external_ids = paper.get("externalIds", {})
                
                pdf_url = ""
                oa = paper.get("openAccessPdf")
                if oa and oa.get("url"):
                    pdf_url = oa["url"]
                elif external_ids.get("ArXiv"):
                    pdf_url = f"https://arxiv.org/pdf/{external_ids['ArXiv']}.pdf"
                
                papers.append(PaperResult(
                    title=paper.get("title", "Unknown"),
                    authors=authors_str or "Unknown",
                    abstract=paper.get("abstract", "") or "",
                    journal=paper.get("journal", {}).get("name", "") if paper.get("journal") else "",
                    year=str(paper.get("year", "")) if paper.get("year") else "",
                    doi=external_ids.get("DOI", ""),
                    pmid=external_ids.get("PubMed", ""),
                    url=paper.get("url", ""),
                    source="Semantic Scholar",
                    citation_count=paper.get("citationCount", 0) or 0,
                    full_text_available=bool(pdf_url),
                    pdf_url=pdf_url
                ))
            
            return papers
        
        except requests.exceptions.Timeout:
            return []
        except requests.exceptions.ConnectionError:
            return []
        except Exception:
            return []