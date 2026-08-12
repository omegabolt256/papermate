"""Unified search engine with caching."""
import time
import json
from typing import List
from pathlib import Path
from .base import PaperResult
from .pubmed_adapter import PubMedAdapter
from .europe_pmc_adapter import EuropePMCAdapter
from .openalex_adapter import OpenAlexAdapter
from .arxiv_adapter import ArxivAdapter
from app.utils import deduplicate_papers
from config.settings import CACHE_DIR

class SearchEngine:
    def __init__(self):
        self.sources = [
            PubMedAdapter(),
            EuropePMCAdapter(),
            OpenAlexAdapter(),
            ArxivAdapter(),
        ]
        self.cache_dir = CACHE_DIR / "searches"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _cache_key(self, query: str) -> str:
        import hashlib
        return hashlib.md5(query.lower().encode()).hexdigest()[:12]
    
    def _get_cached(self, query: str) -> List:
        key = self._cache_key(query)
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            data = json.loads(cache_file.read_text())
            if time.time() - data.get("timestamp", 0) < 86400:
                results = []
                for item in data.get("results", []):
                    results.append(PaperResult(
                        title=item.get("title",""),
                        authors=item.get("authors",""),
                        abstract=item.get("abstract",""),
                        journal=item.get("journal",""),
                        year=item.get("year",""),
                        doi=item.get("doi",""),
                        pmid=item.get("pmid",""),
                        url=item.get("url",""),
                        pdf_url=item.get("pdf_url",""),
                        source=item.get("source",""),
                        full_text_available=item.get("full_text_available",False),
                    ))
                return results
        return None
    
    def _set_cache(self, query: str, results: List):
        key = self._cache_key(query)
        cache_file = self.cache_dir / f"{key}.json"
        cache_file.write_text(json.dumps({
            "query": query,
            "timestamp": time.time(),
            "results": [{
                "title": p.title, "authors": p.authors, "abstract": p.abstract,
                "journal": p.journal, "year": p.year, "doi": p.doi,
                "pmid": p.pmid, "url": p.url, "pdf_url": p.pdf_url,
                "source": p.source, "full_text_available": p.full_text_available
            } for p in results]
        }))
    
    def search(self, query: str, sources: List[str] = None, max_per_source: int = 10) -> List:
        cached = self._get_cached(query)
        if cached:
            print("  (cached results)")
            return cached
        
        all_results = []
        active_sources = self.sources
        if sources:
            active_sources = [s for s in self.sources if s.get_source_name().lower() in [x.lower() for x in sources]]
        
        for source in active_sources:
            try:
                source_name = source.get_source_name()
                print(f"  Searching {source_name}...", end=" ", flush=True)
                results = source.search(query, max_results=max_per_source)
                print(f"found {len(results)}")
                all_results.extend(results)
                time.sleep(1.0)
            except Exception:
                print(f"skipped")
                continue
        
        unique = deduplicate_papers(all_results)
        if unique:
            self._set_cache(query, unique)
        return unique
    
    def search_all(self, query: str, max_per_source: int = 8) -> List:
        return self.search(query, max_per_source=max_per_source)