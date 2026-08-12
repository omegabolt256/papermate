"""arXiv search adapter."""
import re
import urllib.parse
import requests
from typing import List
from .base import LiteratureSource, PaperResult

class ArxivAdapter(LiteratureSource):
    def get_source_name(self) -> str:
        return "arXiv"
    
    def search(self, query: str, max_results: int = 20, **filters) -> List[PaperResult]:
        papers = []
        import time
        time.sleep(0.5)  # Be nice to arXiv
        
        try:
            encoded = urllib.parse.quote(query)
            url = f"http://export.arxiv.org/api/query?search_query=all:{encoded}&max_results={max_results}&sortBy=relevance"
            
            response = requests.get(url, timeout=30)
            entries = response.text.split("<entry>")[1:]
            
            for entry in entries:
                title_m = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
                title = title_m.group(1).strip().replace('\n', ' ') if title_m else "Unknown"
                
                authors = re.findall(r'<name>(.*?)</name>', entry)
                authors_str = ", ".join(authors[:4])
                if len(authors) > 4:
                    authors_str += " et al."
                
                summary_m = re.search(r'<summary>(.*?)</summary>', entry, re.DOTALL)
                abstract = re.sub(r'\s+', ' ', summary_m.group(1).strip()) if summary_m else ""
                
                year_m = re.search(r'<published>(\d{4})', entry)
                year = year_m.group(1) if year_m else ""
                
                id_m = re.search(r'<id>(.*?)</id>', entry)
                arxiv_id = ""
                pdf_url = ""
                paper_url = ""
                if id_m:
                    full = id_m.group(1).strip()
                    aid = re.search(r'abs/([^v]+)', full)
                    if aid:
                        arxiv_id = aid.group(1)
                        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                        paper_url = f"https://arxiv.org/abs/{arxiv_id}"
                
                papers.append(PaperResult(
                    title=title,
                    authors=authors_str or "Unknown",
                    abstract=abstract[:500],
                    year=year,
                    url=paper_url,
                    source="arXiv",
                    full_text_available=True,
                    pdf_url=pdf_url
                ))
            
            return papers
        
        except Exception as e:
            print(f"arXiv error: {e}")
            return []