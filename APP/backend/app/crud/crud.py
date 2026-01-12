from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime

from app.models import models
from app.schemas import schemas

# ========== USER CRUD ==========
def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(
        name=user.name,
        email=user.email,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ========== EMAIL CRUD ==========
def get_email(db: Session, email_id: int) -> Optional[models.Email]:
    return db.query(models.Email).filter(models.Email.id == email_id).first()

def get_emails(db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None, 
               priority: Optional[str] = None) -> List[models.Email]:
    query = db.query(models.Email)
    
    if status:
        query = query.filter(models.Email.status == status)
    if priority:
        query = query.filter(models.Email.priority == priority)
    
    return query.order_by(desc(models.Email.received_at)).offset(skip).limit(limit).all()

def create_email(db: Session, email: schemas.EmailCreate) -> models.Email:
    db_email = models.Email(
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

def update_email(db: Session, email_id: int, email_update: schemas.EmailUpdate) -> Optional[models.Email]:
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
def get_chat_session(db: Session, session_id: int) -> Optional[models.ChatSession]:
    return db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()

def get_chat_session_by_email(db: Session, email_id: int) -> Optional[models.ChatSession]:
    return db.query(models.ChatSession).filter(models.ChatSession.email_id == email_id).first()

def create_chat_session(db: Session, email_id: int) -> models.ChatSession:
    # Check if chat session already exists for this email
    existing = get_chat_session_by_email(db, email_id)
    if existing:
        return existing
    
    db_session = models.ChatSession(email_id=email_id)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    # Update email status to REVIEWING
    email = get_email(db, email_id)
    if email:
        email.status = models.StatusEnum.REVIEWING
        db.commit()
    
    return db_session

# ========== MESSAGE CRUD ==========
def get_messages(db: Session, chat_session_id: int) -> List[models.Message]:
    return db.query(models.Message).filter(
        models.Message.chat_session_id == chat_session_id
    ).order_by(models.Message.created_at).all()

def create_message(db: Session, message: schemas.MessageCreate) -> models.Message:
    db_message = models.Message(
        chat_session_id=message.chat_session_id,
        content=message.content,
        sender=message.sender
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

# ========== DRAFT CRUD ==========
def get_draft(db: Session, draft_id: int) -> Optional[models.Draft]:
    return db.query(models.Draft).filter(models.Draft.id == draft_id).first()

def get_drafts_for_session(db: Session, chat_session_id: int) -> List[models.Draft]:
    return db.query(models.Draft).filter(
        models.Draft.chat_session_id == chat_session_id
    ).order_by(desc(models.Draft.version)).all()

def get_latest_draft(db: Session, chat_session_id: int) -> Optional[models.Draft]:
    return db.query(models.Draft).filter(
        models.Draft.chat_session_id == chat_session_id,
        models.Draft.is_latest == True
    ).first()

def create_draft(db: Session, chat_session_id: int, response_text: str, 
                summary: Optional[str] = None) -> models.Draft:
    # Get version number (increment from latest draft)
    latest = get_latest_draft(db, chat_session_id)
    version = (latest.version + 1) if latest else 1
    
    # Mark previous drafts as not latest
    if latest:
        latest.is_latest = False
    
    db_draft = models.Draft(
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

def update_draft(db: Session, draft_id: int, draft_update: schemas.DraftUpdate) -> Optional[models.Draft]:
    db_draft = get_draft(db, draft_id)
    if not db_draft:
        return None
    
    update_data = draft_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_draft, field, value)
    
    db.commit()
    db.refresh(db_draft)
    return db_draft

def approve_draft(db: Session, draft_id: int, reviewer_id: int) -> Optional[models.Draft]:
    db_draft = get_draft(db, draft_id)
    if not db_draft:
        return None
    
    db_draft.status = models.DraftStatusEnum.APPROVED
    db_draft.reviewed_by = reviewer_id
    db_draft.reviewed_at = datetime.utcnow()
    
    # Update email status to APPROVED
    session = get_chat_session(db, db_draft.chat_session_id)
    if session and session.email:
        session.email.status = models.StatusEnum.APPROVED
    
    db.commit()
    db.refresh(db_draft)
    return db_draft

def reject_draft(db: Session, draft_id: int, reviewer_id: int, reason: Optional[str] = None) -> Optional[models.Draft]:
    db_draft = get_draft(db, draft_id)
    if not db_draft:
        return None
    
    db_draft.status = models.DraftStatusEnum.REJECTED
    db_draft.reviewed_by = reviewer_id
    db_draft.reviewed_at = datetime.utcnow()
    if reason:
        db_draft.regenerate_reason = reason
    
    db.commit()
    db.refresh(db_draft)
    return db_draft

# ========== SOURCE DOCUMENT CRUD ==========
def get_source_document(db: Session, document_id: int) -> Optional[models.SourceDocument]:
    return db.query(models.SourceDocument).filter(models.SourceDocument.id == document_id).first()

def get_source_documents(db: Session, skip: int = 0, limit: int = 100) -> List[models.SourceDocument]:
    return db.query(models.SourceDocument).order_by(
        desc(models.SourceDocument.uploaded_at)
    ).offset(skip).limit(limit).all()

def create_source_document(db: Session, document: schemas.SourceDocumentCreate) -> models.SourceDocument:
    db_document = models.SourceDocument(
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
def get_rating_for_draft(db: Session, draft_id: int) -> Optional[models.EngineerRating]:
    return db.query(models.EngineerRating).filter(
        models.EngineerRating.draft_id == draft_id
    ).first()

def create_rating(db: Session, rating: schemas.EngineerRatingCreate) -> models.EngineerRating:
    db_rating = models.EngineerRating(
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

def update_rating(db: Session, rating_id: int, rating_update: schemas.EngineerRatingBase) -> Optional[models.EngineerRating]:
    db_rating = db.query(models.EngineerRating).filter(models.EngineerRating.id == rating_id).first()
    if not db_rating:
        return None
    
    update_data = rating_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_rating, field, value)
    
    db.commit()
    db.refresh(db_rating)
    return db_rating