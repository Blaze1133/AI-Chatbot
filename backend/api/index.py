from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uuid
import fitz  # PyMuPDF
from typing import Optional, List
from groq import Groq
import cohere
from supabase import create_client, Client

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

# Environment variables
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
COHERE_API_KEY = os.environ.get("COHERE_API_KEY", "")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
MODEL_NAME = os.environ.get("MODEL_NAME", "llama-3.3-70b-versatile")
CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", "200"))

# Initialize clients
supabase_client: Optional[Client] = None
cohere_client: Optional[cohere.Client] = None

if SUPABASE_URL and SUPABASE_KEY:
    supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
if COHERE_API_KEY:
    cohere_client = cohere.Client(COHERE_API_KEY)

class ChatRequest(BaseModel):
    question: str
    document_id: Optional[str] = None

class SourceDocument(BaseModel):
    content: str
    page: int
    filename: str


def extract_text_from_pdf(file_bytes: bytes) -> List[dict]:
    """Extract text from PDF bytes, returning list of {page, content}."""
    pages = []
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text().strip()
        if text:
            pages.append({"page": page_num + 1, "content": text})
    doc.close()
    return pages


def chunk_text_simple(pages: List[dict], document_id: str, filename: str) -> List[dict]:
    """Split pages into chunks with metadata."""
    chunks = []
    for page_info in pages:
        page_num = page_info["page"]
        text = page_info["content"]
        words = text.split()
        
        if len(words) <= CHUNK_SIZE:
            chunks.append({
                "content": text,
                "document_id": document_id,
                "filename": filename,
                "page": page_num,
                "chunk_index": 0
            })
        else:
            start = 0
            chunk_idx = 0
            while start < len(words):
                end = start + CHUNK_SIZE
                chunk_text = " ".join(words[start:end])
                chunks.append({
                    "content": chunk_text,
                    "document_id": document_id,
                    "filename": filename,
                    "page": page_num,
                    "chunk_index": chunk_idx
                })
                start += CHUNK_SIZE - CHUNK_OVERLAP
                chunk_idx += 1
    
    return chunks


def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Get embeddings from Cohere."""
    if not cohere_client:
        raise HTTPException(status_code=503, detail="Cohere client not initialized")
    
    response = cohere_client.embed(
        texts=texts,
        model="embed-english-light-v3.0",
        input_type="search_document"
    )
    return response.embeddings


def ask_groq(question: str, context: str, filename: str) -> str:
    """Send question + context to Groq LLM and return the answer."""
    if not GROQ_API_KEY:
        return (
            "GROQ_API_KEY is not configured on the backend. "
            "Please add it as an environment variable in your Vercel project settings."
        )

    client = Groq(api_key=GROQ_API_KEY)

    system_prompt = (
        "You are a helpful AI document assistant. Answer the user's question based on "
        "the provided document context. Be accurate, concise, and cite specific details "
        "from the document. If the answer is not in the context, say so honestly."
    )

    user_prompt = (
        f"Document: {filename}\n\n"
        f"--- Document Context ---\n{context}\n--- End Context ---\n\n"
        f"Question: {question}\n\n"
        "Please answer based on the document context above."
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        model=MODEL_NAME,
        temperature=0.7,
        max_tokens=1024,
    )

    return chat_completion.choices[0].message.content


@app.get("/")
async def root():
    return {
        "message": "AI Document Assistant API is running",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "supabase_connected": supabase_client is not None,
        "cohere_initialized": cohere_client is not None,
        "groq_initialized": bool(GROQ_API_KEY)
    }

@app.get("/api/test")
async def test():
    return {"message": "Backend API is working!", "deployed": "vercel"}

@app.post("/api/cleanup")
async def cleanup_old_documents():
    """Delete documents older than 30 minutes. Called by Vercel Cron."""
    if not supabase_client:
        raise HTTPException(status_code=503, detail="Supabase not initialized")
    
    try:
        # Delete documents older than 30 minutes
        result = supabase_client.rpc("cleanup_old_documents").execute()
        
        return {
            "message": "Cleanup completed successfully",
            "timestamp": result.data if result.data else "completed"
        }
    except Exception as e:
        # If function doesn't exist, try direct delete (fallback)
        try:
            from datetime import datetime, timedelta
            cutoff_time = (datetime.utcnow() - timedelta(minutes=30)).isoformat()
            
            # Note: This requires created_at column in table
            result = supabase_client.table("documents").delete().lt("created_at", cutoff_time).execute()
            
            return {
                "message": "Cleanup completed (direct delete)",
                "deleted_count": len(result.data) if result.data else 0
            }
        except Exception as fallback_error:
            raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(fallback_error)}")

@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF document and extract its text."""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    if not supabase_client or not cohere_client:
        raise HTTPException(status_code=503, detail="Services not initialized. Please configure SUPABASE_URL, SUPABASE_SERVICE_KEY, and COHERE_API_KEY.")

    document_id = str(uuid.uuid4())

    try:
        file_bytes = await file.read()
        pages = extract_text_from_pdf(file_bytes)

        if not pages:
            raise HTTPException(status_code=400, detail="Could not extract any text from this PDF")

        # Create chunks
        chunks = chunk_text_simple(pages, document_id, file.filename)
        
        # Get embeddings for all chunks
        chunk_texts = [c["content"] for c in chunks]
        embeddings = get_embeddings(chunk_texts)
        
        # Insert into Supabase
        for i, chunk in enumerate(chunks):
            supabase_client.table("documents").insert({
                "content": chunk["content"],
                "metadata": {
                    "document_id": chunk["document_id"],
                    "filename": chunk["filename"],
                    "page": chunk["page"],
                    "chunk_index": chunk["chunk_index"]
                },
                "embedding": embeddings[i]
            }).execute()
        
        return {
            "message": f"Document uploaded successfully. {len(pages)} pages, {len(chunks)} chunks processed.",
            "document_id": document_id,
            "filename": file.filename,
            "pages": len(pages),
            "chunks": len(chunks)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document from vector store."""
    if not supabase_client:
        raise HTTPException(status_code=503, detail="Supabase not initialized")
    
    try:
        # Delete from Supabase using metadata filter
        supabase_client.table("documents").delete().eq("metadata->>document_id", document_id).execute()
        return {"message": "Document deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

@app.post("/api/chat/ask")
async def ask_question(request: ChatRequest):
    """Ask a question about an uploaded document using Groq LLM with vector search."""
    if not supabase_client or not cohere_client:
        raise HTTPException(status_code=503, detail="Services not initialized. Please configure SUPABASE_URL, SUPABASE_SERVICE_KEY, and COHERE_API_KEY.")

    try:
        # Get question embedding
        question_response = cohere_client.embed(
            texts=[request.question],
            model="embed-english-light-v3.0",
            input_type="search_query"
        )
        question_embedding = question_response.embeddings[0]
        
        # Call Supabase RPC function for vector similarity search
        rpc_params = {
            "query_embedding": question_embedding,
            "match_count": 4
        }
        
        if request.document_id:
            rpc_params["filter"] = {"document_id": request.document_id}
        
        result = supabase_client.rpc("match_documents", rpc_params).execute()
        
        if not result.data:
            return {
                "answer": "No relevant information found. Please upload a document first.",
                "source_documents": []
            }

        # Build context from relevant chunks
        context_parts = []
        char_count = 0
        filename = result.data[0]["metadata"].get("filename", "unknown")
        
        for row in result.data:
            content = row["content"]
            page = row["metadata"].get("page", 0)
            
            if char_count + len(content) > 6000:
                remaining = 6000 - char_count
                if remaining > 200:
                    context_parts.append(f"[Page {page}]: {content[:remaining]}...")
                break
            context_parts.append(f"[Page {page}]: {content}")
            char_count += len(content)

        context = "\n\n".join(context_parts)

        # Get AI answer
        answer = ask_groq(request.question, context, filename)

        # Format source documents
        source_documents = [
            {
                "content": row["content"][:300] + ("..." if len(row["content"]) > 300 else ""),
                "page": row["metadata"].get("page", 0),
                "filename": row["metadata"].get("filename", "unknown"),
            }
            for row in result.data
        ]

        return {
            "answer": answer,
            "source_documents": source_documents,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")
