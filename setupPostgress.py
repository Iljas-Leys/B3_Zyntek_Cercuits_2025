from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, create_engine, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DB_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/skilldb"

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ChatResponse(Base):
    __tablename__ = "chat_response"

    id = Column(Integer, primary_key=True, index=True)
    is_question = Column(Boolean)
    text = Column(String)
    rating = Column(Integer, nullable=True)
    generated_at = Column(DateTime)

    session_id = Column(Integer, ForeignKey("session.id"), nullable=False)
    session = relationship("ChatSession", back_populates="responses")

class ChatSession(Base):
    __tablename__ = "session"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime)
    
    responses = relationship("ChatResponse", back_populates="session")

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()