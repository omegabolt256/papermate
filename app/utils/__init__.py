"""Utility functions."""
import re
import hashlib
from typing import List

def deduplicate_papers(papers: List) -> List:
    """Deduplicate papers by DOI, PMID, then title+year."""
    seen_doi = set()
    seen_pmid = set()
    seen_title = set()
    unique = []
    
    for p in papers:
        if p.doi and p.doi in seen_doi:
            continue
        if p.pmid and p.pmid in seen_pmid:
            continue
        
        title_key = f"{p.title.lower()[:100]}_{p.year}"
        if title_key in seen_title:
            continue
        
        if p.doi: seen_doi.add(p.doi)
        if p.pmid: seen_pmid.add(p.pmid)
        seen_title.add(title_key)
        unique.append(p)
    
    return unique

def normalize_doi(doi: str) -> str:
    """Normalize DOI format."""
    doi = doi.strip().lower()
    doi = re.sub(r'^https?://doi\.org/', '', doi)
    return doi

def generate_id(text: str) -> str:
    """Generate a short hash ID."""
    return hashlib.md5(text.encode()).hexdigest()[:12]