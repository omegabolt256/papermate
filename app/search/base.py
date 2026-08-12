"""Base class for literature sources."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class PaperResult:
    title: str
    authors: str
    abstract: str
    journal: str = ""
    year: str = ""
    doi: str = ""
    pmid: str = ""
    pmcid: str = ""
    url: str = ""
    publication_type: str = ""
    keywords: List[str] = field(default_factory=list)
    citation_count: int = 0
    source: str = ""
    full_text_available: bool = False
    pdf_url: str = ""

class LiteratureSource(ABC):
    @abstractmethod
    def search(self, query: str, max_results: int = 20, **filters) -> List[PaperResult]:
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        pass