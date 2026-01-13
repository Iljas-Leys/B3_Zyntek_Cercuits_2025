from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from setupPostgress import SessionLocal, Model, Agent, ChatSession, ChatResponse, engine, Base
import sys
from pathlib import Path

def seed_data():
    db: Session = SessionLocal()

    sample_model = Model(
        path = str(Path(sys.path[0]) / "AI/models/qwen3-4b-q4_k_m.gguf"),
        uploaded_at=datetime.utcnow() - timedelta(days=1),
    )
    db.add(sample_model)
    db.flush()

    physics_agent = Agent(
        created_at=datetime.utcnow() - timedelta(hours=5),
        model_id=sample_model.id,
        vector_domain="example"
    )
    db.add(physics_agent)
    db.flush()

    new_session = ChatSession(
        created_at=datetime.utcnow() - timedelta(minutes=30),
        agent_id=physics_agent.id
    )
    db.add(new_session)
    db.flush()

    q1 = ChatResponse(
        is_question=True,
        text="What is the speed of light?",
        generated_at=datetime.utcnow() - timedelta(minutes=29),
        session_id=new_session.id
    )
    
    a1 = ChatResponse(
        is_question=False,
        text="The speed of light in a vacuum is approximately 299,792,458 meters per second.",
        rating=5,
        generated_at=datetime.utcnow() - timedelta(minutes=28),
        session_id=new_session.id
    )

    db.add_all([q1, a1])
    
    db.commit()
    db.close()

if __name__ == "__main__":
    seed_data()