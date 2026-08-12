"""PubTator data models."""
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

class EntityType(Enum):
    GENE = "Gene"
    DISEASE = "Disease"
    CHEMICAL = "Chemical"
    SPECIES = "Species"
    CELL_LINE = "CellLine"
    MUTATION = "Mutation"
    SNP = "SNP"
    PROTEIN = "Protein"
    DNA = "DNA"
    RNA = "RNA"

@dataclass
class PubTatorEntity:
    """A biomedical entity annotated by PubTator."""
    text: str
    entity_type: str
    identifier: str
    start: int
    end: int
    confidence: Optional[float] = None
    synonyms: List[str] = field(default_factory=list)
    
    def to_dict(self):
        return {
            "text": self.text,
            "type": self.entity_type,
            "identifier": self.identifier,
            "start": self.start,
            "end": self.end,
            "confidence": self.confidence
        }

@dataclass
class PubTatorRelation:
    """A relationship between two entities."""
    subject: str
    relation_type: str
    object: str
    source: str = "PubTator"
    confidence: Optional[float] = None

@dataclass
class PubTatorDocument:
    """A document with PubTator annotations."""
    pmid: str
    title: str
    abstract: str
    entities: List[PubTatorEntity] = field(default_factory=list)
    relations: List[PubTatorRelation] = field(default_factory=list)
    source: str = "PubTator"

@dataclass
class PubTatorSearchResult:
    """Search result from PubTator."""
    pmid: str
    title: str
    snippet: str
    entities: List[PubTatorEntity] = field(default_factory=list)
    score: Optional[float] = None