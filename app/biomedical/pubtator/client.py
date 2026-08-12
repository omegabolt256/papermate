"""Official PubTator 3.0 API client."""
import time
import requests
from typing import List, Optional
from config.settings import NCBI_API_KEY, CACHE_DIR
import json
import hashlib

PUBTATOR_BASE = "https://www.ncbi.nlm.nih.gov/research/pubtator3-api"

class PubTatorClient:
    """
    Client for NCBI PubTator 3.0 API.
    Official documentation: https://www.ncbi.nlm.nih.gov/research/pubtator3/
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or NCBI_API_KEY
        self.base_url = PUBTATOR_BASE
        self.cache_dir = CACHE_DIR / "pubtator"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
    
    def _get_headers(self):
        headers = {"Accept": "application/json"}
        return headers
    
    def _cache_key(self, *args) -> str:
        return hashlib.md5(str(args).encode()).hexdigest()
    
    def _get_cached(self, cache_key: str):
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            with open(cache_file, "r") as f:
                return json.load(f)
        return None
    
    def _set_cache(self, cache_key: str, data):
        cache_file = self.cache_dir / f"{cache_key}.json"
        with open(cache_file, "w") as f:
            json.dump(data, f)
    
    def search(self, query: str, max_results: int = 20, page: int = 1) -> dict:
        """
        Search PubTator for biomedical literature.
        
        Args:
            query: Search query string
            max_results: Maximum number of results
            page: Page number
        
        Returns:
            dict with 'results' list of search results
        """
        cache_key = self._cache_key("search", query, max_results, page)
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        url = f"{self.base_url}/search/"
        params = {
            "text": query,
            "page": page,
            "page_size": max_results
        }
        
        try:
            response = self.session.get(
                url, params=params, headers=self._get_headers(), timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self._set_cache(cache_key, data)
                return data
            elif response.status_code == 429:
                print("PubTator rate limit. Waiting...")
                time.sleep(5)
                return self.search(query, max_results, page)
            else:
                print(f"PubTator search error: HTTP {response.status_code}")
                return {"results": []}
        
        except requests.exceptions.Timeout:
            print("PubTator search timeout")
            return {"results": []}
        except Exception as e:
            print(f"PubTator search error: {e}")
            return {"results": []}
    
    def get_annotations(self, pmids: List[str], concepts: List[str] = None) -> dict:
        """
        Get PubTator annotations for specific PMIDs.
        
        Args:
            pmids: List of PubMed IDs
            concepts: Optional list of concept types (e.g., ["gene", "disease", "chemical"])
        
        Returns:
            dict with BioC JSON format annotations
        """
        if not pmids:
            return {}
        
        pmid_str = ",".join(pmids)
        cache_key = self._cache_key("annotations", pmid_str, str(concepts))
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        url = f"{self.base_url}/publications/export/biocjson"
        params = {"pmids": pmid_str}
        if concepts:
            params["concepts"] = ",".join(concepts)
        
        try:
            response = self.session.get(
                url, params=params, headers=self._get_headers(), timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                self._set_cache(cache_key, data)
                return data
            elif response.status_code == 429:
                print("PubTator rate limit. Waiting...")
                time.sleep(5)
                return self.get_annotations(pmids, concepts)
            else:
                print(f"PubTator annotations error: HTTP {response.status_code}")
                return {}
        
        except Exception as e:
            print(f"PubTator annotations error: {e}")
            return {}
    
    def annotate_text(self, text: str) -> dict:
        """
        Annotate arbitrary biomedical text using PubTator's annotation service.
        
        Note: This sends text to PubTator's API. For local-only mode,
        use a local NER model instead.
        """
        # PubTator primarily works with PMIDs, but we can try the search endpoint
        # which returns annotations in results
        return self.search(text, max_results=1)
    
    def get_entity_types(self) -> List[str]:
        """Get supported entity types from PubTator."""
        return [
            "gene", "disease", "chemical", "species",
            "cellline", "mutation", "snp", "protein",
            "dna", "rna"
        ]