"""Parse PubTator API responses into structured data."""
from typing import List, Dict
from .models import PubTatorEntity, PubTatorDocument, PubTatorSearchResult, PubTatorRelation

class PubTatorParser:
    """Parse PubTator BioC JSON responses into typed models."""
    
    def parse_annotations(self, raw_data: dict) -> List[PubTatorDocument]:
        """
        Parse PubTator BioC JSON into PubTatorDocument objects.
        
        Expected input: PubTator 3.0 API response
        """
        documents = []
        
        if not raw_data:
            return documents
        
        # Handle both single document and list
        items = raw_data if isinstance(raw_data, list) else [raw_data]
        
        for item in items:
            try:
                doc = self._parse_single_document(item)
                if doc:
                    documents.append(doc)
            except Exception as e:
                print(f"Parse error: {e}")
                continue
        
        return documents
    
    def _parse_single_document(self, item: dict) -> PubTatorDocument:
        """Parse a single BioC document."""
        pmid = str(item.get("pmid", item.get("id", "unknown")))
        
        # Get title and abstract from passages
        title = ""
        abstract = ""
        passages = item.get("passages", [])
        
        for passage in passages:
            passage_type = passage.get("infons", {}).get("type", "")
            text = passage.get("text", "")
            
            if passage_type == "title":
                title = text
            elif passage_type == "abstract":
                abstract = text
        
        # Extract entities from annotations
        entities = []
        for passage in passages:
            for annotation in passage.get("annotations", []):
                entity = self._parse_annotation(annotation, passage.get("text", ""))
                if entity:
                    entities.append(entity)
        
        # Extract relations
        relations = []
        for passage in passages:
            for relation in passage.get("relations", []):
                rel = self._parse_relation(relation)
                if rel:
                    relations.append(rel)
        
        return PubTatorDocument(
            pmid=pmid,
            title=title,
            abstract=abstract,
            entities=entities,
            relations=relations
        )
    
    def _parse_annotation(self, annotation: dict, full_text: str) -> PubTatorEntity:
        """Parse a single BioC annotation."""
        infons = annotation.get("infons", {})
        locations = annotation.get("locations", [{}])
        
        entity_type = infons.get("type", "unknown")
        identifier = infons.get("identifier", "")
        text = annotation.get("text", "")
        
        # Get position from locations
        start = locations[0].get("offset", 0) if locations else 0
        length = locations[0].get("length", len(text)) if locations else len(text)
        end = start + length
        
        return PubTatorEntity(
            text=text,
            entity_type=entity_type,
            identifier=identifier,
            start=start,
            end=end,
            confidence=infons.get("confidence")
        )
    
    def _parse_relation(self, relation: dict) -> PubTatorRelation:
        """Parse a single BioC relation."""
        infons = relation.get("infons", {})
        nodes = relation.get("nodes", [])
        
        relation_type = infons.get("type", "associated_with")
        
        subject = ""
        obj = ""
        if len(nodes) >= 2:
            subject = nodes[0].get("refid", "")
            obj = nodes[1].get("refid", "")
        
        return PubTatorRelation(
            subject=subject,
            relation_type=relation_type,
            object=obj,
            confidence=infons.get("confidence")
        )
    
    def parse_search_results(self, raw_data: dict) -> List[PubTatorSearchResult]:
        """Parse PubTator search results."""
        results = []
        
        for item in raw_data.get("results", []):
            entities = []
            for ann in item.get("annotations", []):
                infons = ann.get("infons", {})
                entities.append(PubTatorEntity(
                    text=ann.get("text", ""),
                    entity_type=infons.get("type", ""),
                    identifier=infons.get("identifier", ""),
                    start=ann.get("start", 0),
                    end=ann.get("end", 0)
                ))
            
            results.append(PubTatorSearchResult(
                pmid=str(item.get("pmid", "")),
                title=item.get("title", ""),
                snippet=item.get("snippet", ""),
                entities=entities,
                score=item.get("score")
            ))
        
        return results