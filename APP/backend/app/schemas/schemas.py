from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

# ========== ENUMS ==========
class StatusEnum(str, Enum):
    NEW = "new"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    SENT = "sent"

class PriorityEnum(str, Enum):
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class CategoryEnum(str, Enum):
    BIOS = "BIOS"
    HARDWARE = "Hardware"
    DRIVERS = "Drivers"

class DraftStatusEnum(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"

# ========== USER SCHEMAS ==========
class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: Optional[str] = "engineer"

class UserCreate(UserBase):
    pass

class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# ========== EMAIL SCHEMAS ==========
class EmailBase(BaseModel):
    from_email: EmailStr
    subject: str
    body: str
    category: Optional[CategoryEnum] = CategoryEnum.HARDWARE
    priority: Optional[PriorityEnum] = PriorityEnum.MEDIUM

class EmailCreate(EmailBase):
    pass

class EmailUpdate(BaseModel):
    status: Optional[StatusEnum] = None
    priority: Optional[PriorityEnum] = None
    assigned_to: Optional[int] = None

class EmailOut(EmailBase):
    id: int
    received_at: datetime
    resolved_at: Optional[datetime] = None
    status: StatusEnum
    assigned_to: Optional[int] = None
    
    class Config:
        from_attributes = True

class EmailWithSession(EmailOut):
    chat_session: Optional['ChatSessionOut'] = None
    
    class Config:
        from_attributes = True

# ========== CHAT SESSION SCHEMAS ==========
class ChatSessionBase(BaseModel):
    email_id: int

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionOut(ChatSessionBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatSessionDetail(ChatSessionOut):
    email: EmailOut
    messages: List['MessageOut'] = []
    drafts: List['DraftOut'] = []
    
    class Config:
        from_attributes = True

# ========== MESSAGE SCHEMAS ==========
class MessageBase(BaseModel):
    content: str
    sender: str  # "user" or "ai"

class MessageCreate(MessageBase):
    chat_session_id: int

class MessageOut(MessageBase):
    id: int
    chat_session_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ========== DRAFT SCHEMAS ==========
class DraftBase(BaseModel):
    response_text: str
    summary: Optional[str] = None

class DraftCreate(DraftBase):
    chat_session_id: int

class DraftUpdate(BaseModel):
    response_text: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[DraftStatusEnum] = None

class DraftOut(DraftBase):
    id: int
    chat_session_id: int
    version: int
    is_latest: bool
    status: DraftStatusEnum
    generated_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[int] = None
    feedback_score: Optional[int] = None
    
    class Config:
        from_attributes = True

class DraftWithSources(DraftOut):
    source_documents: List['SourceDocumentOut'] = []
    
    class Config:
        from_attributes = True

# ========== SOURCE DOCUMENT SCHEMAS ==========
class SourceDocumentBase(BaseModel):
    title: str
    file_name: str
    file_type: str
    category: Optional[str] = None
    tags: Optional[str] = None

class SourceDocumentCreate(SourceDocumentBase):
    uploaded_by: int
    file_url: Optional[str] = None

class SourceDocumentOut(SourceDocumentBase):
    id: int
    uploaded_at: datetime
    last_indexed_at: Optional[datetime] = None
    uploaded_by: Optional[int] = None
    
    class Config:
        from_attributes = True

# ========== ENGINEER RATING SCHEMAS ==========
class EngineerRatingBase(BaseModel):
    rating_score: int = Field(..., ge=1, le=5)
    accuracy_score: Optional[int] = Field(None, ge=1, le=5)
    completeness_score: Optional[int] = Field(None, ge=1, le=5)
    usefulness_score: Optional[int] = Field(None, ge=1, le=5)
    comments: Optional[str] = None

class EngineerRatingCreate(EngineerRatingBase):
    draft_id: int
    engineer_id: int

class EngineerRatingOut(EngineerRatingBase):
    id: int
    draft_id: int
    engineer_id: Optional[int] = None
    rated_at: datetime
    
    class Config:
        from_attributes = True

# ========== MISC SCHEMAS ==========
class GenerateDraftRequest(BaseModel):
    chat_session_id: int
    additional_context: Optional[str] = None

class ApproveDraftRequest(BaseModel):
    draft_id: int
    reviewer_id: int

class HealthCheck(BaseModel):
    status: str
    timestamp: datetime

# Update forward references
ChatSessionDetail.model_rebuild()
EmailWithSession.model_rebuild()
DraftWithSources.model_rebuild()