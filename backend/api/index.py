import sys
import os

# Add backend to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import routes
from app.routes import documents, chat, session

# Create FastAPI app
app = FastAPI(title="AI Document Assistant API",
    description="AI-powered document question answering system",
    version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(session.router)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "AI Document Assistant API is running", "session_based": True}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "session_storage": True}

# For Vercel serverless
def handler(request):
    return app(request)
