from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app import schemas, crud

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))
from setupPostgress import Email, StatusEnum, Draft, DraftStatusEnum, StatusEnum

router = APIRouter()

# ========================================
# USER ENDPOINTS
# ========================================

@router.get("/users", response_model=List[schemas.UserOut])
def list_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get list of all users"""
    return crud.get_users(db, skip=skip, limit=limit)

@router.get("/users/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get single user by ID"""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users", response_model=schemas.UserOut, status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create new user"""
    # Check if email already exists
    existing = crud.get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user)

# ========================================
# EMAIL ENDPOINTS
# ========================================

@router.get("/emails", response_model=List[schemas.EmailOut])
def list_emails(
    skip: int = 0, 
    limit: int = 100,
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    db: Session = Depends(get_db)
):
    """Get list of all emails with optional filters"""
    return crud.get_emails(db, skip=skip, limit=limit, status=status, priority=priority)

@router.get("/emails/{email_id}", response_model=schemas.EmailWithSession)
def get_email(email_id: int, db: Session = Depends(get_db)):
    """Get single email by ID (includes chat session if exists)"""
    email = crud.get_email(db, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email

@router.post("/emails", response_model=schemas.EmailOut, status_code=201)
def create_email(email: schemas.EmailCreate, db: Session = Depends(get_db)):
    """Create new email (simulating incoming customer email)"""
    return crud.create_email(db, email)

@router.patch("/emails/{email_id}", response_model=schemas.EmailOut)
def update_email(
    email_id: int, 
    email_update: schemas.EmailUpdate, 
    db: Session = Depends(get_db)
):
    """Update email status, priority, or assignment"""
    email = crud.update_email(db, email_id, email_update)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email

@router.delete("/emails/{email_id}", status_code=204)
def delete_email(email_id: int, db: Session = Depends(get_db)):
    """Delete an email"""
    success = crud.delete_email(db, email_id)
    if not success:
        raise HTTPException(status_code=404, detail="Email not found")
    return None

# ========================================
# CHAT SESSION ENDPOINTS
# ========================================

@router.post("/emails/{email_id}/chat-session", response_model=schemas.ChatSessionOut, status_code=201)
def create_chat_session(email_id: int, db: Session = Depends(get_db)):
    """
    Open/create a chat session for an email
    Returns existing session if one already exists
    """
    # Verify email exists
    email = crud.get_email(db, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    return crud.create_chat_session(db, email_id)

@router.get("/chat-sessions/{session_id}", response_model=schemas.ChatSessionDetail)
def get_chat_session(session_id: int, db: Session = Depends(get_db)):
    """Get chat session with all messages and drafts"""
    session = crud.get_chat_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session

# ========================================
# MESSAGE ENDPOINTS
# ========================================

@router.get("/chat-sessions/{session_id}/messages", response_model=List[schemas.MessageOut])
def list_messages(session_id: int, db: Session = Depends(get_db)):
    """Get all messages in a chat session"""
    # Verify session exists
    session = crud.get_chat_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    return crud.get_messages(db, session_id)

@router.post("/messages", response_model=schemas.MessageOut, status_code=201)
def create_message(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    """Add a message to a chat session"""
    # Verify session exists
    session = crud.get_chat_session(db, message.chat_session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    return crud.create_message(db, message)

# ========================================
# DRAFT ENDPOINTS
# ========================================

@router.get("/chat-sessions/{session_id}/drafts", response_model=List[schemas.DraftOut])
def list_drafts(session_id: int, db: Session = Depends(get_db)):
    """Get all drafts for a chat session"""
    session = crud.get_chat_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    return crud.get_drafts_for_session(db, session_id)

@router.get("/drafts/{draft_id}", response_model=schemas.DraftWithSources)
def get_draft(draft_id: int, db: Session = Depends(get_db)):
    """Get single draft by ID (includes source documents)"""
    draft = crud.get_draft(db, draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return draft

@router.post("/chat-sessions/{session_id}/generate-draft", response_model=schemas.DraftOut, status_code=201)
def generate_draft(
    session_id: int,
    additional_context: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Generate AI draft response for a chat session
    MVP: Returns mock response (LLM integration comes later)
    """
    # Verify session exists
    session = crud.get_chat_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    # MVP: Mock AI response
    email = session.email
    mock_response = f"""Thank you for contacting CERcuits technical support.

Regarding your inquiry about: "{email.subject}"

Based on your description, I recommend the following steps:

1. Check the BIOS settings and verify that all configurations match the specifications in the documentation
2. Ensure all drivers are up to date
3. Verify that the hardware components are properly seated and connected

If the issue persists after these steps, please provide:
- System logs
- Hardware revision numbers
- Any error codes you're encountering

This will help us diagnose the issue more accurately.

Best regards,
CERcuits Technical Support

[Note: This is a MOCK response for MVP testing. AI integration pending.]
"""
    
    summary = f"Troubleshooting steps for {email.category.value} issue"
    
    return crud.create_draft(db, session_id, mock_response, summary)

@router.patch("/drafts/{draft_id}", response_model=schemas.DraftOut)
def update_draft(
    draft_id: int,
    draft_update: schemas.DraftUpdate,
    db: Session = Depends(get_db)
):
    """Update a draft (e.g., manual edits)"""
    draft = crud.update_draft(db, draft_id, draft_update)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return draft

@router.post("/drafts/{draft_id}/approve", response_model=schemas.DraftOut)
def approve_draft(
    draft_id: int,
    reviewer_id: int = Query(..., description="ID of the reviewing engineer"),
    db: Session = Depends(get_db)
):
    """Approve a draft response"""
    draft = crud.approve_draft(db, draft_id, reviewer_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return draft

@router.post("/drafts/{draft_id}/reject", response_model=schemas.DraftOut)
def reject_draft(
    draft_id: int,
    reviewer_id: int = Query(..., description="ID of the reviewing engineer"),
    reason: Optional[str] = Query(None, description="Reason for rejection"),
    db: Session = Depends(get_db)
):
    """Reject a draft response"""
    draft = crud.reject_draft(db, draft_id, reviewer_id, reason)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return draft

# ========================================
# SOURCE DOCUMENT ENDPOINTS
# ========================================

@router.get("/documents", response_model=List[schemas.SourceDocumentOut])
def list_documents(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get list of all knowledge base documents"""
    return crud.get_source_documents(db, skip=skip, limit=limit)

@router.get("/documents/{document_id}", response_model=schemas.SourceDocumentOut)
def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get single document by ID"""
    document = crud.get_source_document(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.post("/documents", response_model=schemas.SourceDocumentOut, status_code=201)
def create_document(document: schemas.SourceDocumentCreate, db: Session = Depends(get_db)):
    """Upload a new knowledge base document (metadata only for MVP)"""
    return crud.create_source_document(db, document)

@router.delete("/documents/{document_id}", status_code=204)
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document"""
    success = crud.delete_source_document(db, document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return None

# ========================================
# ENGINEER RATING ENDPOINTS
# ========================================

@router.get("/drafts/{draft_id}/rating", response_model=schemas.EngineerRatingOut)
def get_rating(draft_id: int, db: Session = Depends(get_db)):
    """Get rating for a draft"""
    rating = crud.get_rating_for_draft(db, draft_id)
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    return rating

@router.post("/ratings", response_model=schemas.EngineerRatingOut, status_code=201)
def create_rating(rating: schemas.EngineerRatingCreate, db: Session = Depends(get_db)):
    """Create a quality rating for a draft"""
    # Check if draft exists
    draft = crud.get_draft(db, rating.draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    
    # Check if rating already exists
    existing = crud.get_rating_for_draft(db, rating.draft_id)
    if existing:
        raise HTTPException(status_code=400, detail="Rating already exists for this draft")
    
    return crud.create_rating(db, rating)

# ========================================
# STATISTICS / DASHBOARD ENDPOINTS
# ========================================

@router.get("/stats/summary")
def get_stats_summary(db: Session = Depends(get_db)):
    """Get high-level statistics for dashboard"""
    total_emails = db.query(Email).count()
    new_emails = db.query(Email).filter(Email.status == StatusEnum.NEW).count()
    reviewing_emails = db.query(Email).filter(Email.status == StatusEnum.REVIEWING).count()
    approved_emails = db.query(Email).filter(Email.status == StatusEnum.APPROVED).count()
    sent_emails = db.query(Email).filter(Email.status == StatusEnum.SENT).count()
    
    total_drafts = db.query(Draft).count()
    approved_drafts = db.query(Draft).filter(Draft.status == DraftStatusEnum.APPROVED).count()
    
    return {
        "total_emails": total_emails,
        "emails_by_status": {
            "new": new_emails,
            "reviewing": reviewing_emails,
            "approved": approved_emails,
            "sent": sent_emails
        },
        "total_drafts": total_drafts,
        "approved_drafts": approved_drafts,
        "draft_approval_rate": round(approved_drafts / total_drafts * 100, 2) if total_drafts > 0 else 0
    }