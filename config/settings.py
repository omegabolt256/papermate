"""Application settings loaded from environment variables."""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / ".env")

# AI Model
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/data/research.db")

# Vector Store
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", str(BASE_DIR / "data" / "indexes"))

# Data Directories
DATA_DIR = Path(os.getenv("DATA_DIR", "D:/Projects/PaperMate/data"))
PAPERS_DIR = DATA_DIR / "papers"
LIBRARY_DIR = DATA_DIR / "library"
CACHE_DIR = DATA_DIR / "cache"

# API Keys (all optional)
PUBMED_EMAIL = os.getenv("PUBMED_EMAIL", "")
NCBI_API_KEY = os.getenv("NCBI_API_KEY", "")
SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
OPENALEX_EMAIL = os.getenv("OPENALEX_EMAIL", "")
ZOTERO_API_KEY = os.getenv("ZOTERO_API_KEY", "4fTByCdt05xKM7An6pJhCdd8")
ZOTERO_USER_ID = os.getenv("ZOTERO_USER_ID", "21071663")

# Create directories
for d in [DATA_DIR, PAPERS_DIR, LIBRARY_DIR, CACHE_DIR, Path(VECTOR_DB_PATH)]:
    d.mkdir(parents=True, exist_ok=True)