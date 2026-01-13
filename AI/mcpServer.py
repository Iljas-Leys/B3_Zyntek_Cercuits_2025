# ↓ To run without inspector, use mcpTests.txt to run the MCP server with a test client
# .\.venv\Scripts\activate
# python .\AI\mcpServer.py

from mcp.server.fastmcp import FastMCP
from redis import Redis
from redisvl.index import SearchIndex
from datetime import datetime, timezone
from sqlalchemy.orm import joinedload
import ollama

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from setupPostgress import SessionLocal, ChatSession, ChatResponse, Agent, Model

client = Redis.from_url("redis://localhost:6379")
index = SearchIndex.from_yaml("redisSchema.yaml", redis_client = client, validate_on_load = True)

mcp = FastMCP("mcp_server")

if __name__ == "__main__":
    print("This terminal runs the MCP server. Please keep it open.")
    mcp.run()

@mcp.tool()
async def store_text(text: str) -> bool:
    return True

@mcp.tool()
async def create_session(agent_id_: str) -> int:
    with SessionLocal() as db:
        new_session = ChatSession(
            created_at=datetime.utcnow(),
            agent_id = agent_id_,
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        return new_session.id

@mcp.tool()
async def create_agent(model_path_: str, vector_domain_: str = "") -> bool:
    with SessionLocal() as db:
        new_agent = Agent(
            created_at=datetime.utcnow(),
            model_path = model_path_,
            vector_domain = vector_domain_,
        )
        db.add(new_agent)
        db.commit()
        db.refresh(new_agent)
        return new_agent.id

@mcp.prompt()
async def ask_question(question: str, session_id: str):
    with SessionLocal() as db:
        session = db.query(ChatSession).options(
            joinedload(ChatSession.agent).joinedload(Agent.model)
        ).filter(ChatSession.id == int(session_id)).first()

        if not session:
            return f"Error: Session {session_id} not found."

        # 1. Get ONLY the filename from your DB (e.g., 'qwen3-4b-q4_k_m.gguf')
        # This ignores whatever C:\ path you have stored and just grabs the file name
        filename = Path(session.agent.model.path).name
        
        # 2. Point to the path INSIDE the Docker container Linux system
        docker_path = f"/models/{filename}"
        
        # 3. Ensure the model name is lowercase for Ollama
        ollama_model_name = f"model_{session.agent.id}".lower()

        try:
            filename = Path(session.agent.model.path).name
            docker_path = f"/models/{filename}"
            ollama_model_name = f"model-{session.agent.id}".lower()

            # The 'from_' argument is the preferred way in recent ollama-python versions
            # to handle local GGUF files. 
            ollama.create(
                model=ollama_model_name,
                from_=docker_path
            )

            # If 'from_' also gives an error, the only other valid keyword is 'modelfile'
            # but some versions require it to be passed like this:
            # ollama.create(model=ollama_model_name, modelfile=f"FROM {docker_path}")

            response = ollama.chat(
                model=ollama_model_name, 
                messages=[{'role': 'user', 'content': question}]
            )
            ai_response_text = response['message']['content']
            
        except Exception as e:
            ai_response_text = f"Ollama Error: {str(e)}"

        # 4. Save to DB
        now = datetime.now(timezone.utc)
        user_msg = ChatResponse(session_id=session.id, is_question=True, text=question, generated_at=now)
        ai_msg = ChatResponse(session_id=session.id, is_question=False, text=ai_response_text, generated_at=now)
        
        db.add_all([user_msg, ai_msg])
        db.commit()
        
        return ai_response_text