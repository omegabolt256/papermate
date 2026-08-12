"""
Literature Research Adapter

Provides research synthesis capabilities using public APIs.
Designed to be replaced with official The LITERATURE API when available.
"""
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from app.search.engine import SearchEngine
from app.search.base import PaperResult
from app.biomedical.pubtator.service import PubTatorService
from app.models import get_model_provider

@dataclass
class ResearchFindings:
    """Structured research findings."""
    query: str
    papers: List[PaperResult] = field(default_factory=list)
    key_findings: List[str] = field(default_factory=list)
    entities: Dict[str, list] = field(default_factory=dict)
    contradictions: List[str] = field(default_factory=list)
    research_gaps: List[str] = field(default_factory=list)
    summary: str = ""
    references: List[str] = field(default_factory=list)

class LiteratureAdapter:
    """
    Research adapter compatible with The LITERATURE's workflow.
    Uses PubMed, Semantic Scholar, PubTator, and local AI.
    """
    
    def __init__(self):
        self.search_engine = SearchEngine()
        self.pubtator = PubTatorService()
        self.model = get_model_provider("ollama")
    
    def research(self, question: str, max_papers: int = 10) -> ResearchFindings:
        """
        Perform multi-step literature research.
        
        Args:
            question: Research question
            max_papers: Maximum papers to retrieve
        
        Returns:
            ResearchFindings with structured results
        """
        findings = ResearchFindings(query=question)
        
        # Step 1: Search literature
        print(f"  Searching literature for: {question}")
        papers = self.search_engine.search_all(question, max_per_source=max_papers)
        findings.papers = papers[:max_papers]
        
        if not papers:
            findings.summary = "No papers found."
            return findings
        
        # Step 2: Get PMIDs for PubTator
        pmids = [p.pmid for p in papers if p.pmid]
        
        # Step 3: Extract biomedical entities
        if pmids:
            print(f"  Extracting biomedical entities from {len(pmids)} papers...")
            try:
                entities_data = self.pubtator.extract_entities_from_pmids(pmids[:10])
                findings.entities = entities_data
            except Exception as e:
                print(f"  PubTator error: {e}")
        
        # Step 4: Synthesize findings with AI
        print("  Synthesizing findings...")
        findings = self._synthesize(findings)
        
        return findings
    
    def _synthesize(self, findings: ResearchFindings) -> ResearchFindings:
        """Use AI to synthesize research findings."""
        
        # Build context from papers
        context_parts = []
        for i, paper in enumerate(findings.papers[:8], 1):
            context_parts.append(
                f"[{i}] {paper.title}\n"
                f"    Authors: {paper.authors}\n"
                f"    Year: {paper.year}\n"
                f"    Abstract: {paper.abstract[:300]}\n"
            )
        
        context = "\n".join(context_parts)
        
        # Prompt for structured analysis
        prompt = f"""You are a medical research analyst. Analyze the following papers and answer the research question.

RESEARCH QUESTION: {findings.query}

PAPERS:
{context}

Provide a structured analysis with these sections:

KEY FINDINGS:
- List the main findings from the papers

CONTRADICTIONS (if any):
- Note any conflicting results between studies

RESEARCH GAPS:
- Identify what questions remain unanswered

SUMMARY:
- A 3-5 sentence summary of the current evidence

RULES:
- Only use information from the papers above
- Cite papers as [1], [2], etc.
- If evidence is lacking, say so
- Never fabricate findings

ANALYSIS:"""
        
        try:
            response = self.model.generate(prompt, max_tokens=800)
            
            # Parse the response into sections
            sections = response.split("\n\n")
            
            current_section = ""
            for line in response.split("\n"):
                line = line.strip()
                if line.startswith("KEY FINDINGS"):
                    current_section = "findings"
                elif line.startswith("CONTRADICTIONS"):
                    current_section = "contradictions"
                elif line.startswith("RESEARCH GAPS"):
                    current_section = "gaps"
                elif line.startswith("SUMMARY"):
                    current_section = "summary"
                elif line.startswith("- ") and current_section == "findings":
                    findings.key_findings.append(line[2:])
                elif line.startswith("- ") and current_section == "contradictions":
                    findings.contradictions.append(line[2:])
                elif line.startswith("- ") and current_section == "gaps":
                    findings.research_gaps.append(line[2:])
            
            findings.summary = sections[-1] if sections else response[:500]
        
        except Exception as e:
            findings.summary = f"AI synthesis unavailable: {e}"
        
        # Generate references
        for i, paper in enumerate(findings.papers[:10], 1):
            ref = f"[{i}] {paper.authors} ({paper.year}). {paper.title}."
            if paper.doi:
                ref += f" DOI: {paper.doi}"
            if paper.pmid:
                ref += f" PMID: {paper.pmid}"
            findings.references.append(ref)
        
        return findings
    
    def search_only(self, question: str, max_papers: int = 10) -> List[PaperResult]:
        """Quick search without full synthesis."""
        return self.search_engine.search_all(question, max_per_source=max_papers)