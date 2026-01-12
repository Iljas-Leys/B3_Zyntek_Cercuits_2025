# ↓ To run without inspector, use mcpTests.txt to run the MCP server with a test client
# .\.venv\Scripts\activate
# python .\AI\mcpServer.py

from mcp.server.fastmcp import FastMCP
from redis import Redis
from redisvl.index import SearchIndex
from datetime import datetime

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from setupPostgress import SessionLocal, ChatSession, ChatResponse

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
async def create_chat_session() -> int:
    with SessionLocal() as db:
        new_session = ChatSession(
            created_at=datetime.utcnow()
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        return new_session.id

@mcp.prompt()
async def ask_question(question: str, session_id: str):
    # Later, AI will be used to generate a response
    ai_response_text = "response"
    with SessionLocal() as db:
        user_msg = ChatResponse(
            session_id=session_id,
            is_question=True,
            text=question,
            generated_at=datetime.utcnow()
        )
        db.add(user_msg)
        
        ai_msg = ChatResponse(
            session_id=session_id,
            is_question=False,
            text=ai_response_text,
            generated_at=datetime.utcnow()
        )
        db.add(ai_msg)
        
        db.commit()
        
        return ai_response_text