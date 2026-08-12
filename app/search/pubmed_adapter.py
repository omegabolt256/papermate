"""PubMed search adapter."""
import time
import requests
from typing import List
from .base import LiteratureSource, PaperResult
from config.settings import PUBMED_EMAIL, NCBI_API_KEY

class PubMedAdapter(LiteratureSource):
    def get_source_name(self) -> str:
        return "PubMed"

    def search(self, query: str, max_results: int = 20, **filters) -> List[PaperResult]:
        papers = []
        import time
        time.sleep(0.5)  # NCBI rate limit: 3/sec        
        try:
            # Build search parameters
            params = {
                "db": "pubmed",
                "term": query,
                "retmax": max_results,
                "retmode": "json",
                "sort": "relevance"
            }
            if NCBI_API_KEY:
                params["api_key"] = NCBI_API_KEY
            if PUBMED_EMAIL:
                params["email"] = PUBMED_EMAIL
            
            # Search
            url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            ids = data.get("esearchresult", {}).get("idlist", [])
            
            if not ids:
                return []
            
            # Get summaries
            time.sleep(0.34)  # NCBI rate limit: 3/sec without API key
            summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            summary_params = {
                "db": "pubmed",
                "id": ",".join(ids),
                "retmode": "json"
            }
            if NCBI_API_KEY:
                summary_params["api_key"] = NCBI_API_KEY
            
            response = requests.get(summary_url, params=summary_params, timeout=10)
            data = response.json()
            
            for pid in ids:
                info = data.get("result", {}).get(pid, {})
                if not info or "title" not in info:
                    continue
                
                authors = [a.get("name", "") for a in info.get("authors", [])]
                authors_str = ", ".join(authors[:4])
                if len(authors) > 4:
                    authors_str += " et al."
                
                # Get identifiers
                pmc_id = ""
                doi = ""
                for aid in info.get("articleids", []):
                    if aid.get("idtype") == "pmc":
                        pmc_id = aid.get("value", "")
                    if aid.get("idtype") == "doi":
                        doi = aid.get("value", "")
                
                pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/pdf/" if pmc_id else ""
                
                papers.append(PaperResult(
                    title=info.get("title", "Unknown"),
                    authors=authors_str,
                    abstract=f"PubMed ID: {pid}",
                    journal=info.get("source", ""),
                    year=info.get("pubdate", "")[:4] or "",
                    doi=doi,
                    pmid=pid,
                    pmcid=pmc_id,
                    url=f"https://pubmed.ncbi.nlm.nih.gov/{pid}/",
                    source="PubMed",
                    full_text_available=bool(pmc_id),
                    pdf_url=pdf_url
                ))
            
            return papers
        
        except Exception as e:
            print(f"PubMed error: {e}")
            return []