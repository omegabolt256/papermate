"""OpenAlex search adapter – free, no key, all fields."""
import requests
from typing import List
from .base import LiteratureSource, PaperResult

class OpenAlexAdapter(LiteratureSource):
    def get_source_name(self) -> str:
        return "OpenAlex"

    def search(self, query: str, max_results: int = 20, **filters) -> List[PaperResult]:
        papers = []
        try:
            url = "https://api.openalex.org/works"
            params = {
                "search": query,
                "per_page": max_results,
                "sort": "cited_by_count:desc",
            }
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            
            for item in data.get("results", []):
                # Authors
                authors = []
                for a in item.get("authorships", []):
                    author = a.get("author", {})
                    name = author.get("display_name", "")
                    if name:
                        authors.append(name)
                authors_str = ", ".join(authors[:4])
                if len(authors) > 4:
                    authors_str += " et al."
                
                # IDs
                ids = item.get("ids", {})
                doi = ids.get("doi", "").replace("https://doi.org/", "") if ids.get("doi") else ""
                pmid = str(ids.get("pmid", "")) if ids.get("pmid") else ""
                
                # PDF
                pdf_url = ""
                oa = item.get("open_access", {})
                if oa.get("is_oa"):
                    pdf_url = oa.get("pdf_url", "") or ""
                
                # Journal
                journal = ""
                loc = item.get("primary_location", {})
                if loc:
                    src = loc.get("source", {})
                    journal = src.get("display_name", "") if src else ""
                
                # Year
                year = str(item.get("publication_year", ""))
                
                # Abstract
                abstract = ""
                if item.get("abstract_inverted_index"):
                    # Try to reconstruct abstract from inverted index
                    try:
                        inv = item["abstract_inverted_index"]
                        words = [""] * max([pos for positions in inv.values() for pos in positions]) if inv else []
                        for word, positions in inv.items():
                            for pos in positions:
                                if pos < len(words):
                                    words[pos] = word
                        abstract = " ".join(words)
                    except:
                        pass
                
                papers.append(PaperResult(
                    title=item.get("title", "Unknown"),
                    authors=authors_str or "Unknown",
                    abstract=abstract[:500],
                    journal=journal,
                    year=year,
                    doi=doi,
                    pmid=pmid,
                    url=item.get("id", ""),
                    source="OpenAlex",
                    citation_count=item.get("cited_by_count", 0) or 0,
                    full_text_available=bool(pdf_url),
                    pdf_url=pdf_url,
                ))
            return papers
        except Exception:
            return []