from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum, Boolean, Float, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base

# ========== ENUMS ==========
class StatusEnum(str, enum.Enum):
    NEW = "new"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    SENT = "sent"

class PriorityEnum(str, enum.Enum):
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class CategoryEnum(str, enum.Enum):
    BIOS = "BIOS"
    HARDWARE = "Hardware"
    DRIVERS = "Drivers"

class DraftStatusEnum(str, enum.Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"

# ========== ASSOCIATION TABLES ==========
# Many-to-many relationship between Draft and SourceDocument
draft_sources = Table(
    'draft_sources',
    Base.metadata,
    Column('draft_id', Integer, ForeignKey('drafts.id', ondelete='CASCADE'), primary_key=True),
    Column('source_document_id', Integer, ForeignKey('source_documents.id', ondelete='CASCADE'), primary_key=True),
    Column('relevance_score', Float, nullable=True)
)

# ========== MODELS ==========

class User(Base):
    """Specialist/Engineer user"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    role = Column(String, default="engineer")  # engineer, admin, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    assigned_emails = relationship("Email", back_populates="assigned_user", foreign_keys="Email.assigned_to")
    reviewed_drafts = relationship("Draft", back_populates="reviewer", foreign_keys="Draft.reviewed_by")
    uploaded_documents = relationship("SourceDocument", back_populates="uploader")
    engineer_ratings = relationship("EngineerRating", back_populates="engineer")


class Email(Base):
    """Customer email/inquiry"""
    __tablename__ = "emails"
    
    id = Column(Integer, primary_key=True, index=True)
    from_email = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    received_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)
    
    # Classification
    category = Column(Enum(CategoryEnum), default=CategoryEnum.HARDWARE)
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.MEDIUM, index=True)
    status = Column(Enum(StatusEnum), default=StatusEnum.NEW, index=True)
    
    # Assignment
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    assigned_user = relationship("User", back_populates="assigned_emails", foreign_keys=[assigned_to])
    chat_session = relationship("ChatSession", back_populates="email", uselist=False, cascade="all, delete-orphan")


class ChatSession(Base):
    """Chat session for handling an email inquiry"""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey("emails.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    email = relationship("Email", back_populates="chat_session")
    messages = relationship("Message", back_populates="chat_session", cascade="all, delete-orphan", order_by="Message.created_at")
    drafts = relationship("Draft", back_populates="chat_session", cascade="all, delete-orphan", order_by="Draft.version")


class Message(Base):
    """Individual message in a chat session"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    sender = Column(String, nullable=False)  # "user" or "ai"
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    chat_session = relationship("ChatSession", back_populates="messages")
    source_documents = relationship("SourceDocument", back_populates="message")


class Draft(Base):
    """AI-generated draft response"""
    __tablename__ = "drafts"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Content
    response_text = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    
    # Versioning
    version = Column(Integer, default=1)
    is_latest = Column(Boolean, default=True)
    regenerate_reason = Column(Text, nullable=True)
    
    # Status and review
    status = Column(Enum(DraftStatusEnum), default=DraftStatusEnum.DRAFT, index=True)
    generated_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    feedback_score = Column(Integer, nullable=True)  # 1-5 rating
    
    # Relationships
    chat_session = relationship("ChatSession", back_populates="drafts")
    reviewer = relationship("User", back_populates="reviewed_drafts", foreign_keys=[reviewed_by])
    source_documents = relationship("SourceDocument", secondary=draft_sources, back_populates="drafts")
    engineer_rating = relationship("EngineerRating", back_populates="draft", uselist=False, cascade="all, delete-orphan")


class SourceDocument(Base):
    """Knowledge base document"""
    __tablename__ = "source_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # File information
    title = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # pdf, docx, txt, etc.
    file_url = Column(String, nullable=True)  # Path to stored file
    content_hash = Column(String, nullable=True, index=True)  # For duplicate detection
    
    # Metadata
    category = Column(String, nullable=True)
    tags = Column(Text, nullable=True)  # JSON array stored as text
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    last_indexed_at = Column(DateTime, nullable=True)  # When it was last chunked/embedded
    
    # Uploader
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Link to message (if document was attached to a specific message)
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    uploader = relationship("User", back_populates="uploaded_documents")
    message = relationship("Message", back_populates="source_documents")
    drafts = relationship("Draft", secondary=draft_sources, back_populates="source_documents")


class EngineerRating(Base):
    """Quality rating given by engineer to a draft"""
    __tablename__ = "engineer_ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    draft_id = Column(Integer, ForeignKey("drafts.id", ondelete="CASCADE"), nullable=False, unique=True)
    engineer_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Rating data
    rating_score = Column(Integer, nullable=False)  # 1-5
    accuracy_score = Column(Integer, nullable=True)  # 1-5
    completeness_score = Column(Integer, nullable=True)  # 1-5
    usefulness_score = Column(Integer, nullable=True)  # 1-5
    
    # Feedback
    comments = Column(Text, nullable=True)
    rated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    draft = relationship("Draft", back_populates="engineer_rating")
    engineer = relationship("User", back_populates="engineer_ratings", foreign_keys=[engineer_id])