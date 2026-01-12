# ↓ To run without inspector, use mcpTests.txt to run the MCP server with a test client
# .\.venv\Scripts\activate
# python .\AI\mcpServer.py

from mcp.server.fastmcp import FastMCP
from redis import Redis
from redisvl.index import SearchIndex

client = Redis.from_url("redis://localhost:6379")
index = SearchIndex.from_yaml("redisSchema.yaml", redis_client = client, validate_on_load = True)

mcp = FastMCP("mcp_server")

if __name__ == "__main__":
    mcp.run()

@mcp.tool()
async def store_text(text: str) -> bool:
    return True
