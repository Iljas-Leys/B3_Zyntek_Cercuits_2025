from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime

# from app.models import models
import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from setupPostgress import User, Email, ChatSession, StatusEnum, PriorityEnum, CategoryEnum, DraftStatusEnum, Message, Draft, SourceDocument, EngineerRating
from app.schemas import schemas

# ========== USER CRUD ==========
def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate) -> User:
    db_user = User(
        name=user.name,
        email=user.email,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ========== EMAIL CRUD ==========
def get_email(db: Session, email_id: int) -> Optional[Email]:
    return db.query(Email).filter(Email.id == email_id).first()

def get_emails(db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None, 
               priority: Optional[str] = None) -> List[Email]:
    query = db.query(Email)
    
    if status:
        query = query.filter(Email.status == status)
    if priority:
        query = query.filter(Email.priority == priority)
    
    return query.order_by(desc(Email.received_at)).offset(skip).limit(limit).all()

def create_email(db: Session, email: schemas.EmailCreate) -> Email:
    db_email = Email(
        from_email=email.from_email,
        subject=email.subject,
        body=email.body,
        category=email.category,
        priority=email.priority
    )
    db.add(db_email)
    db.commit()
    db.refresh(db_email)
    return db_email

def update_email(db: Session, email_id: int, email_update: schemas.EmailUpdate) -> Optional[Email]:
    db_email = get_email(db, email_id)
    if not db_email:
        return None
    
    update_data = email_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_email, field, value)
    
    db.commit()
    db.refresh(db_email)
    return db_email

def delete_email(db: Session, email_id: int) -> bool:
    db_email = get_email(db, email_id)
    if not db_email:
        return False
    db.delete(db_email)
    db.commit()
    return True

# ========== CHAT SESSION CRUD ==========
def get_chat_session(db: Session, session_id: int) -> Optional[ChatSession]:
    return db.query(ChatSession).filter(ChatSession.id == session_id).first()

def get_chat_session_by_email(db: Session, email_id: int) -> Optional[ChatSession]:
    return db.query(ChatSession).filter(ChatSession.email_id == email_id).first()

def create_chat_session(db: Session, email_id: int) -> ChatSession:
    # Check if chat session already exists for this email
    existing = get_chat_session_by_email(db, email_id)
    if existing:
        return existing
    
    db_session = ChatSession(email_id=email_id)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    # Update email status to REVIEWING
    email = get_email(db, email_id)
    if email:
        email.status = StatusEnum.REVIEWING
        db.commit()
    
    return db_session

# ========== MESSAGE CRUD ==========
def get_messages(db: Session, chat_session_id: int) -> List[Message]:
    return db.query(Message).filter(
        Message.chat_session_id == chat_session_id
    ).order_by(Message.created_at).all()

def create_message(db: Session, message: schemas.MessageCreate) -> Message:
    db_message = Message(
        chat_session_id=message.chat_session_id,
        content=message.content,
        sender=message.sender
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

# ========== DRAFT CRUD ==========
def get_draft(db: Session, draft_id: int) -> Optional[Draft]:
    return db.query(Draft).filter(Draft.id == draft_id).first()

def get_drafts_for_session(db: Session, chat_session_id: int) -> List[Draft]:
    return db.query(Draft).filter(
        Draft.chat_session_id == chat_session_id
    ).order_by(desc(Draft.version)).all()

def get_latest_draft(db: Session, chat_session_id: int) -> Optional[Draft]:
    return db.query(Draft).filter(
        Draft.chat_session_id == chat_session_id,
        Draft.is_latest == True
    ).first()

def create_draft(db: Session, chat_session_id: int, response_text: str, 
                summary: Optional[str] = None) -> Draft:
    # Get version number (increment from latest draft)
    latest = get_latest_draft(db, chat_session_id)
    version = (latest.version + 1) if latest else 1
    
    # Mark previous drafts as not latest
    if latest:
        latest.is_latest = False
    
    db_draft = Draft(
        chat_session_id=chat_session_id,
        response_text=response_text,
        summary=summary,
        version=version,
        is_latest=True
    )
    db.add(db_draft)
    db.commit()
    db.refresh(db_draft)
    return db_draft

def update_draft(db: Session, draft_id: int, draft_update: schemas.DraftUpdate) -> Optional[Draft]:
    db_draft = get_draft(db, draft_id)
    if not db_draft:
        return None
    
    update_data = draft_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_draft, field, value)
    
    db.commit()
    db.refresh(db_draft)
    return db_draft

def approve_draft(db: Session, draft_id: int, reviewer_id: int) -> Optional[Draft]:
    db_draft = get_draft(db, draft_id)
    if not db_draft:
        return None
    
    db_draft.status = DraftStatusEnum.APPROVED
    db_draft.reviewed_by = reviewer_id
    db_draft.reviewed_at = datetime.utcnow()
    
    # Update email status to APPROVED
    session = get_chat_session(db, db_draft.chat_session_id)
    if session and session.email:
        session.email.status = StatusEnum.APPROVED
    
    db.commit()
    db.refresh(db_draft)
    return db_draft

def reject_draft(db: Session, draft_id: int, reviewer_id: int, reason: Optional[str] = None) -> Optional[Draft]:
    db_draft = get_draft(db, draft_id)
    if not db_draft:
        return None
    
    db_draft.status = DraftStatusEnum.REJECTED
    db_draft.reviewed_by = reviewer_id
    db_draft.reviewed_at = datetime.utcnow()
    if reason:
        db_draft.regenerate_reason = reason
    
    db.commit()
    db.refresh(db_draft)
    return db_draft

# ========== SOURCE DOCUMENT CRUD ==========
def get_source_document(db: Session, document_id: int) -> Optional[SourceDocument]:
    return db.query(SourceDocument).filter(SourceDocument.id == document_id).first()

def get_source_documents(db: Session, skip: int = 0, limit: int = 100) -> List[SourceDocument]:
    return db.query(SourceDocument).order_by(
        desc(SourceDocument.uploaded_at)
    ).offset(skip).limit(limit).all()

def create_source_document(db: Session, document: schemas.SourceDocumentCreate) -> SourceDocument:
    db_document = SourceDocument(
        title=document.title,
        file_name=document.file_name,
        file_type=document.file_type,
        file_url=document.file_url,
        category=document.category,
        tags=document.tags,
        uploaded_by=document.uploaded_by
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def delete_source_document(db: Session, document_id: int) -> bool:
    db_document = get_source_document(db, document_id)
    if not db_document:
        return False
    db.delete(db_document)
    db.commit()
    return True

# ========== ENGINEER RATING CRUD ==========
def get_rating_for_draft(db: Session, draft_id: int) -> Optional[EngineerRating]:
    return db.query(EngineerRating).filter(
        EngineerRating.draft_id == draft_id
    ).first()

def create_rating(db: Session, rating: schemas.EngineerRatingCreate) -> EngineerRating:
    db_rating = EngineerRating(
        draft_id=rating.draft_id,
        engineer_id=rating.engineer_id,
        rating_score=rating.rating_score,
        accuracy_score=rating.accuracy_score,
        completeness_score=rating.completeness_score,
        usefulness_score=rating.usefulness_score,
        comments=rating.comments
    )
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating

def update_rating(db: Session, rating_id: int, rating_update: schemas.EngineerRatingBase) -> Optional[EngineerRating]:
    db_rating = db.query(EngineerRating).filter(EngineerRating.id == rating_id).first()
    if not db_rating:
        return None
    
    update_data = rating_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_rating, field, value)
    
    db.commit()
    db.refresh(db_rating)
    return db_rating