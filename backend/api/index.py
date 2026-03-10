from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uuid
from typing import Optional, List

app = FastAPI(
    title="AI Document Assistant API",
    description="AI-powered document question answering system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo (will be replaced with proper storage)
documents_store = {}

class ChatRequest(BaseModel):
    question: str
    document_id: Optional[str] = None

class SourceDocument(BaseModel):
    content: str
    page: int
    filename: str

@app.get("/")
async def root():
    return {
        "message": "AI Document Assistant API is running",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/test")
async def test():
    return {"message": "Backend API is working!", "deployed": "vercel"}

@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF document"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Generate unique document ID
    document_id = str(uuid.uuid4())
    
    # Store document metadata (in production, save file and process it)
    documents_store[document_id] = {
        "filename": file.filename,
        "document_id": document_id,
        "content": f"Sample content from {file.filename}"
    }
    
    return {
        "message": "Document uploaded successfully",
        "document_id": document_id,
        "filename": file.filename
    }

@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document"""
    if document_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    del documents_store[document_id]
    return {"message": "Document deleted successfully"}

@app.post("/api/chat/ask")
async def ask_question(request: ChatRequest):
    """Ask a question about a document"""
    if request.document_id and request.document_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Demo response (will be replaced with actual AI processing)
    doc_info = documents_store.get(request.document_id, {})
    filename = doc_info.get("filename", "unknown")
    
    answer = f"This is a demo response to your question: '{request.question}'. "
    answer += f"The backend is working! Document: {filename}. "
    answer += "Full AI integration with Groq will be added next."
    
    return {
        "answer": answer,
        "source_documents": [
            {
                "content": f"Sample content from {filename}",
                "page": 1,
                "filename": filename
            }
        ]
    }
