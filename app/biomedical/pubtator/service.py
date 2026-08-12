"""High-level PubTator service combining client and parser."""
from typing import List, Optional
from .client import PubTatorClient
from .parser import PubTatorParser
from .models import PubTatorDocument, PubTatorSearchResult, PubTatorEntity

class PubTatorService:
    """Service for biomedical entity recognition via PubTator."""
    
    def __init__(self, api_key: str = None):
        self.client = PubTatorClient(api_key)
        self.parser = PubTatorParser()
    
    def search_biomedical(self, query: str, max_results: int = 20) -> List[PubTatorSearchResult]:
        """Search PubTator and return parsed results."""
        raw = self.client.search(query, max_results)
        return self.parser.parse_search_results(raw)
    
    def annotate_papers(self, pmids: List[str]) -> List[PubTatorDocument]:
        """Get full annotations for papers by PMID."""
        raw = self.client.get_annotations(pmids)
        return self.parser.parse_annotations(raw)
    
    def get_entities_for_paper(self, pmid: str) -> List[PubTatorEntity]:
        """Get all entities for a single paper."""
        docs = self.annotate_papers([pmid])
        if docs:
            return docs[0].entities
        return []
    
    def get_entities_grouped(self, pmid: str) -> dict:
        """Get entities grouped by type."""
        entities = self.get_entities_for_paper(pmid)
        grouped = {}
        for entity in entities:
            etype = entity.entity_type.lower()
            if etype not in grouped:
                grouped[etype] = []
            grouped[etype].append(entity)
        return grouped
    
    def annotate_local_text(self, text: str) -> List[PubTatorEntity]:
        """
        Annotate local text using PubTator.
        For best results, use this with text that contains
        biomedical terms likely recognized by PubTator.
        """
        raw = self.client.annotate_text(text)
        results = self.parser.parse_search_results(raw)
        if results:
            return results[0].entities
        return []
    
    def extract_entities_from_pmids(self, pmids: List[str]) -> dict:
        """
        Extract all entities from multiple papers.
        
        Returns:
            dict mapping pmid -> dict of entity_type -> list of entities
        """
        all_entities = {}
        docs = self.annotate_papers(pmids)
        
        for doc in docs:
            grouped = {}
            for entity in doc.entities:
                etype = entity.entity_type.lower()
                if etype not in grouped:
                    grouped[etype] = []
                grouped[etype].append(entity.to_dict())
            all_entities[doc.pmid] = grouped
        
        return all_entities