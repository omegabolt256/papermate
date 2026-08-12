"""SQLAlchemy database models - Extended with Projects, Chats, Notes."""
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, Float, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from config.settings import DATABASE_URL
import uuid

Base = declarative_base()

def generate_id():
    return uuid.uuid4().hex[:12]

# ==================== PROJECTS ====================

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, default=generate_id)
    serial_number = Column(Integer, nullable=True, unique=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    research_question = Column(Text, default="")
    status = Column(String, default="active")  # active, archived, completed
    tags = Column(JSON, default=list)
    settings = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_opened_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    papers = relationship("Paper", back_populates="project", cascade="all, delete-orphan")
    chats = relationship("Chat", back_populates="project", cascade="all, delete-orphan")
    searches = relationship("Search", back_populates="project", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="project", cascade="all, delete-orphan")
    evidence = relationship("Evidence", back_populates="project", cascade="all, delete-orphan")
    screening_decisions = relationship("ScreeningDecision", back_populates="project", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "serial_number": self.serial_number,
            "name": self.name,
            "description": self.description,
            "research_question": self.research_question,
            "status": self.status,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_opened_at": self.last_opened_at.isoformat() if self.last_opened_at else None,
            "paper_count": len(self.papers),
            "chat_count": len(self.chats),
        }

# ==================== PAPERS ====================

class Paper(Base):
    __tablename__ = "papers"
    
    id = Column(String, primary_key=True, default=generate_id)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    
    # Metadata
    title = Column(String, default="Unknown")
    authors = Column(Text, default="")
    abstract = Column(Text, default="")
    journal = Column(String, default="")
    year = Column(String, default="")
    doi = Column(String, default="")
    pmid = Column(String, default="")
    pmcid = Column(String, default="")
    url = Column(String, default="")
    pdf_url = Column(String, default="")
    source = Column(String, default="")
    
    # File
    pdf_path = Column(String, default="")
    file_size = Column(Integer, default=0)
    full_text_available = Column(Boolean, default=False)
    
    # Status
    read_status = Column(String, default="unread")  # unread, reading, read
    importance = Column(String, default="")  # important, review, critical
    tags = Column(JSON, default=list)
    
    # Screening
    screening_status = Column(String, default="unscreened")  # unscreened, included, excluded, maybe
    screening_round = Column(Integer, default=0)
    screening_notes = Column(Text, default="")
    
    # Timestamps
    added_at = Column(DateTime, default=datetime.utcnow)
    downloaded_at = Column(DateTime, nullable=True)
    indexed_at = Column(DateTime, nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="papers")
    chunks = relationship("Chunk", back_populates="paper", cascade="all, delete-orphan")
    entities = relationship("Entity", back_populates="paper", cascade="all, delete-orphan")
    paper_notes = relationship("PaperNote", back_populates="paper", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract[:200] if self.abstract else "",
            "journal": self.journal,
            "year": self.year,
            "doi": self.doi,
            "pmid": self.pmid,
            "source": self.source,
            "pdf_path": self.pdf_path,
            "full_text_available": self.full_text_available,
            "read_status": self.read_status,
            "screening_status": self.screening_status,
            "tags": self.tags,
            "added_at": self.added_at.isoformat() if self.added_at else None,
        }

# ==================== CHUNKS ====================

class Chunk(Base):
    __tablename__ = "chunks"
    
    id = Column(String, primary_key=True, default=generate_id)
    paper_id = Column(String, ForeignKey("papers.id"), nullable=False)
    text = Column(Text, default="")
    page_number = Column(Integer, default=1)
    section = Column(String, default="")
    chunk_index = Column(Integer, default=0)
    embedding_id = Column(String, default="")
    
    paper = relationship("Paper", back_populates="chunks")

# ==================== CHATS ====================

class Chat(Base):
    __tablename__ = "chats"
    
    id = Column(String, primary_key=True, default=generate_id)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    title = Column(String, default="New Chat")
    model = Column(String, default="mistral")
    context_type = Column(String, default="project")  # project, paper, comparison
    context_papers = Column(JSON, default=list)  # list of paper IDs
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = relationship("Project", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan", order_by="Message.timestamp")
    
    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "title": self.title,
            "model": self.model,
            "message_count": len(self.messages),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=generate_id)
    chat_id = Column(String, ForeignKey("chats.id"), nullable=False)
    role = Column(String, default="user")  # user, assistant, system
    content = Column(Text, default="")
    sources = Column(JSON, default=list)  # [{paper_id, title, page, quote}]
    entities = Column(JSON, default=list)
    tool_calls = Column(JSON, default=list)
    extra_metadata = Column(JSON, default=dict)
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    chat = relationship("Chat", back_populates="messages")
    
    def to_dict(self):
        return {
            "id": self.id,
            "chat_id": self.chat_id,
            "role": self.role,
            "content": self.content,
            "sources": self.sources,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }

# ==================== SEARCHES ====================

class Search(Base):
    __tablename__ = "searches"
    
    id = Column(String, primary_key=True, default=generate_id)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    query = Column(Text, default="")
    sources = Column(JSON, default=list)
    filters = Column(JSON, default=dict)
    results_count = Column(Integer, default=0)
    results_cache = Column(JSON, default=list)
    research_mode = Column(String, default="quick")  # quick, deep, biomedical
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="searches")
    
    def to_dict(self):
        return {
            "id": self.id,
            "query": self.query,
            "sources": self.sources,
            "results_count": self.results_count,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }

# ==================== NOTES ====================

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(String, primary_key=True, default=generate_id)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    title = Column(String, default="")
    content = Column(Text, default="")
    note_type = Column(String, default="general")  # general, paper, evidence, method
    tags = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = relationship("Project", back_populates="notes")

class PaperNote(Base):
    __tablename__ = "paper_notes"
    
    id = Column(String, primary_key=True, default=generate_id)
    paper_id = Column(String, ForeignKey("papers.id"), nullable=False)
    page_number = Column(Integer, nullable=True)
    selected_text = Column(Text, default="")
    note_content = Column(Text, default="")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    paper = relationship("Paper", back_populates="paper_notes")

# ==================== EVIDENCE ====================

class Evidence(Base):
    __tablename__ = "evidence"
    
    id = Column(String, primary_key=True, default=generate_id)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    paper_id = Column(String, ForeignKey("papers.id"), nullable=False)
    category = Column(String, default="")
    field = Column(String, default="")
    value = Column(Text, default="")
    confidence = Column(Float, default=0.0)
    source_type = Column(String, default="ai_extracted")  # ai_extracted, human_verified, original
    
    extracted_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="evidence")

# ==================== SCREENING ====================

class ScreeningDecision(Base):
    __tablename__ = "screening_decisions"
    
    id = Column(String, primary_key=True, default=generate_id)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    paper_id = Column(String, ForeignKey("papers.id"), nullable=False)
    decision = Column(String, default="unscreened")  # include, exclude, maybe
    reason = Column(Text, default="")
    ai_suggestion = Column(String, default="")
    ai_confidence = Column(Float, default=0.0)
    user_override = Column(Boolean, default=False)
    screening_round = Column(Integer, default=1)
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="screening_decisions")

# ==================== ENTITIES ====================

class Entity(Base):
    __tablename__ = "entities"
    
    id = Column(String, primary_key=True, default=generate_id)
    paper_id = Column(String, ForeignKey("papers.id"), nullable=False)
    name = Column(String, default="")
    entity_type = Column(String, default="")  # gene, disease, chemical, species, etc.
    identifier = Column(String, default="")
    synonyms = Column(JSON, default=list)
    confidence = Column(Float, default=0.0)
    source = Column(String, default="PubTator")  # PubTator, local_model, manual
    
    paper = relationship("Paper", back_populates="entities")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.entity_type,
            "identifier": self.identifier,
            "source": self.source,
        }

# ==================== SETTINGS ====================

class AppSettings(Base):
    __tablename__ = "app_settings"
    
    key = Column(String, primary_key=True)
    value = Column(Text, default="")
    updated_at = Column(DateTime, default=datetime.utcnow)

# ==================== DATABASE SETUP ====================

engine = create_engine(DATABASE_URL, echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def get_session():
    return Session()