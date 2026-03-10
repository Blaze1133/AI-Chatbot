from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uuid
import fitz  # PyMuPDF
from typing import Optional, List
from groq import Groq

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

# In-memory storage for documents and their extracted text
documents_store = {}

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
MODEL_NAME = os.environ.get("MODEL_NAME", "llama-3.3-70b-versatile")

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


def find_relevant_chunks(pages: List[dict], question: str, top_k: int = 3) -> List[dict]:
    """Simple keyword-based relevance search across pages."""
    question_words = set(question.lower().split())
    scored = []
    for p in pages:
        content_lower = p["content"].lower()
        score = sum(1 for w in question_words if w in content_lower)
        scored.append((score, p))
    scored.sort(key=lambda x: x[0], reverse=True)
    # Return top_k pages, but always return at least the first page if nothing matches
    results = [item[1] for item in scored[:top_k] if item[0] > 0]
    if not results and pages:
        results = [pages[0]]
    return results


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
    return {"status": "healthy"}

@app.get("/api/test")
async def test():
    return {"message": "Backend API is working!", "deployed": "vercel"}

@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF document and extract its text."""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    document_id = str(uuid.uuid4())

    try:
        file_bytes = await file.read()
        pages = extract_text_from_pdf(file_bytes)

        if not pages:
            raise HTTPException(status_code=400, detail="Could not extract any text from this PDF")

        documents_store[document_id] = {
            "filename": file.filename,
            "document_id": document_id,
            "pages": pages,
            "full_text": "\n\n".join(p["content"] for p in pages),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

    return {
        "message": "Document uploaded successfully",
        "document_id": document_id,
        "filename": file.filename
    }

@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document."""
    if document_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found")

    del documents_store[document_id]
    return {"message": "Document deleted successfully"}

@app.post("/api/chat/ask")
async def ask_question(request: ChatRequest):
    """Ask a question about an uploaded document using Groq LLM."""
    if request.document_id and request.document_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found. Please upload a document first.")

    doc_info = documents_store.get(request.document_id, {})
    filename = doc_info.get("filename", "unknown")
    pages = doc_info.get("pages", [])

    # Find relevant chunks
    relevant = find_relevant_chunks(pages, request.question, top_k=3)

    # Build context from relevant pages (limit to ~6000 chars to stay within token limits)
    context_parts = []
    char_count = 0
    for chunk in relevant:
        if char_count + len(chunk["content"]) > 6000:
            remaining = 6000 - char_count
            if remaining > 200:
                context_parts.append(f"[Page {chunk['page']}]: {chunk['content'][:remaining]}...")
            break
        context_parts.append(f"[Page {chunk['page']}]: {chunk['content']}")
        char_count += len(chunk["content"])

    context = "\n\n".join(context_parts) if context_parts else "No document content available."

    try:
        answer = ask_groq(request.question, context, filename)
    except Exception as e:
        answer = f"Sorry, I encountered an error processing your question: {str(e)}"

    source_documents = [
        {
            "content": chunk["content"][:300] + ("..." if len(chunk["content"]) > 300 else ""),
            "page": chunk["page"],
            "filename": filename,
        }
        for chunk in relevant
    ]

    return {
        "answer": answer,
        "source_documents": source_documents,
    }
