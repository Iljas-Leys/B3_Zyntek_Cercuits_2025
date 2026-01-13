from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, create_engine, ForeignKey, String
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
    
    agent_id = Column(Integer, ForeignKey("agent.id"), nullable=False)

    agent = relationship("Agent", back_populates="sessions")
    responses = relationship("ChatResponse", back_populates="session")

class Agent(Base):
    __tablename__ = "agent"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime)
    vector_domain = Column(String)

    model_id = Column(Integer, ForeignKey("model.id"), nullable=False)

    sessions = relationship("ChatSession", back_populates="agent")
    model = relationship("Model", back_populates="agents")

class Model(Base):
    __tablename__ = "model"

    id = Column(Integer, primary_key=True, index=True)
    uploaded_at = Column(DateTime)
    path = Column(String)

    agents = relationship("Agent", back_populates="model")


def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()