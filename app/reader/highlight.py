"""Highlight text in PDFs and ask AI about it."""
import fitz
import os
from typing import Dict, Optional
from app.models import get_model_provider

class HighlightAnalyzer:
    """Analyze highlighted text with AI."""
    
    def __init__(self):
        self.model = get_model_provider("ollama")
    
    def get_text_from_pdf(self, pdf_path: str, page: int, start: int, end: int) -> str:
        """Get text from a specific region of a PDF page."""
        try:
            doc = fitz.open(pdf_path)
            if page - 1 < len(doc):
                page_obj = doc[page - 1]
                text = page_obj.get_text()
                doc.close()
                return text[start:end].strip()
            doc.close()
        except:
            pass
        return ""
    
    def explain_highlight(self, pdf_path: str, page: int, selected_text: str, 
                          context: str = "", paper_title: str = "") -> str:
        """Explain why this text is important."""
        prompt = f"""You are a medical research assistant. A researcher highlighted this text from a paper.

PAPER: {paper_title or 'Research paper'}
PAGE: {page}
HIGHLIGHTED TEXT:
"{selected_text}"

SURROUNDING CONTEXT:
"{context[:500]}"

Please:
1. EXPLAIN what this means in simple terms
2. WHY it might be important (significance)
3. HOW it relates to the broader research
4. Any KEY TERMS that should be noted
5. SUGGEST related questions to explore

Be concise but informative."""
        
        try:
            return self.model.generate(prompt, max_tokens=400)
        except:
            return "AI unavailable. Try again when Ollama is running."
    
    def summarize_highlight(self, selected_text: str) -> str:
        """Quick one-sentence summary of highlighted text."""
        prompt = f"""Summarize this research text in one clear sentence:

"{selected_text[:500]}"

One-sentence summary:"""
        
        try:
            return self.model.generate(prompt, max_tokens=100)
        except:
            return selected_text[:200] + "..."
    
    def extract_data_from_highlight(self, selected_text: str) -> Dict:
        """Extract structured data from highlighted text."""
        prompt = f"""Extract key data points from this research text as JSON:

TEXT:
"{selected_text[:500]}"

Return a JSON object with these fields (use null if not found):
{{
    "compound": "chemical/compound name",
    "concentration": "dosage/concentration",
    "method": "method/technique used",
    "result": "key result/finding",
    "p_value": "statistical significance if mentioned",
    "organism": "organism/cell line tested",
    "endpoint": "what was measured"
}}

JSON:"""
        
        try:
            response = self.model.generate(prompt, max_tokens=300)
            import json
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except:
            pass
        return {}
    
    def suggest_related_papers(self, selected_text: str) -> str:
        """Suggest what to search for based on highlighted text."""
        prompt = f"""Based on this research text, suggest 3 specific search queries 
to find related papers:

TEXT: "{selected_text[:300]}"

Return as:
1. [search query]
2. [search query]
3. [search query]"""
        
        try:
            return self.model.generate(prompt, max_tokens=150)
        except:
            return "Search suggestions unavailable."
    
    def ask_about_highlight(self, pdf_path: str, page: int, 
                            selected_text: str, question: str,
                            paper_title: str = "") -> str:
        """Ask a specific question about highlighted text."""
        prompt = f"""A researcher highlighted this text and has a question.

PAPER: {paper_title or 'Research paper'}
PAGE: {page}
HIGHLIGHTED TEXT:
"{selected_text}"

QUESTION: {question}

Answer based on the highlighted text and general knowledge.
If the answer isn't in the text, say so clearly."""
        
        try:
            return self.model.generate(prompt, max_tokens=400)
        except:
            return "AI unavailable."