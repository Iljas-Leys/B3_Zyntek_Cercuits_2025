from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine, Base
from app.api import endpoints

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Agent TSE API",
    description="AI-assisted technical support system for CERcuits",
    version="0.1.0"
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(endpoints.router, prefix="/api", tags=["agent-tse"])

@app.get("/")
def root():
    return {
        "message": "Agent TSE API is running",
        "docs": "/docs",
        "version": "0.1.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}