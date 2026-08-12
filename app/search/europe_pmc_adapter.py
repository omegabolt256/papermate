"""Europe PMC search adapter – no API key needed, biomedical focus."""
import requests
from typing import List
from .base import LiteratureSource, PaperResult

class EuropePMCAdapter(LiteratureSource):
    def get_source_name(self) -> str:
        return "Europe PMC"

    def search(self, query: str, max_results: int = 20, **filters) -> List[PaperResult]:
        papers = []
        try:
            url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
            params = {
                "query": query,
                "resultType": "core",
                "pageSize": max_results,
                "format": "json",
            }
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            for item in data.get("resultList", {}).get("result", []):
                authors_str = item.get("authorString", "")
                authors = authors_str.split(", ") if authors_str else []
                authors_short = ", ".join(authors[:4])
                if len(authors) > 4:
                    authors_short += " et al."

                pdf_url = ""
                if item.get("pmcid"):
                    pdf_url = f"https://europepmc.org/articles/{item['pmcid']}/pdf"

                papers.append(PaperResult(
                    title=item.get("title", "Unknown"),
                    authors=authors_short or "Unknown",
                    abstract=item.get("abstractText", "")[:500],
                    journal=item.get("journalTitle", ""),
                    year=item.get("pubYear", ""),
                    doi=item.get("doi", ""),
                    pmid=item.get("pmid", ""),
                    pmcid=item.get("pmcid", ""),
                    url=f"https://europepmc.org/article/MED/{item.get('pmid','')}" if item.get("pmid") else "",
                    source="Europe PMC",
                    full_text_available=bool(pdf_url),
                    pdf_url=pdf_url,
                ))
            return papers
        except Exception:
            return []