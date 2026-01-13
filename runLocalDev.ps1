. .\.venv\Scripts\Activate.ps1

# Run MCP server
Start-Process powershell -ArgumentList"-NoExit", "-Command", "& .\.venv\Scripts\python.exe AI/mcpServer.py"

# Run backend
#Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd APP/backend; & ../../.venv/Scripts/python.exe -m uvicorn app.main:app --reload"

pause