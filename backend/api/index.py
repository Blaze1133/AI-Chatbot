from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uuid
import fitz  # PyMuPDF
from typing import Optional, List
from groq import Groq
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

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
CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", "100"))

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


def chunk_text(pages: List[dict], chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[dict]:
    """Split page text into overlapping chunks for better semantic retrieval."""
    chunks = []
    for page_info in pages:
        text = page_info["content"]
        page_num = page_info["page"]
        words = text.split()
        if len(words) <= chunk_size:
            chunks.append({"page": page_num, "content": text})
        else:
            start = 0
            while start < len(words):
                end = start + chunk_size
                chunk_text = " ".join(words[start:end])
                chunks.append({"page": page_num, "content": chunk_text})
                start += chunk_size - overlap
    return chunks


def semantic_search(chunks: List[dict], question: str, top_k: int = 3) -> List[dict]:
    """TF-IDF based semantic search - finds chunks most similar to the question."""
    if not chunks:
        return []

    corpus = [c["content"] for c in chunks]
    corpus.append(question)  # Add question as last element

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),  # Unigrams and bigrams for better semantic matching
        max_features=5000,
    )
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # Compute cosine similarity between question (last) and all chunks
    question_vec = tfidf_matrix[-1]
    chunk_vecs = tfidf_matrix[:-1]
    similarities = cosine_similarity(question_vec, chunk_vecs).flatten()

    # Get top_k indices sorted by similarity
    top_indices = np.argsort(similarities)[::-1][:top_k]

    results = []
    for idx in top_indices:
        if similarities[idx] > 0.0:  # Only include chunks with some relevance
            results.append({
                **chunks[idx],
                "score": float(similarities[idx]),
            })

    # Fallback: if no semantic match, return first chunk
    if not results and chunks:
        results = [{**chunks[0], "score": 0.0}]

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

        chunks = chunk_text(pages)

        documents_store[document_id] = {
            "filename": file.filename,
            "document_id": document_id,
            "pages": pages,
            "chunks": chunks,
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
    chunks = doc_info.get("chunks", [])

    # Semantic search using TF-IDF cosine similarity
    relevant = semantic_search(chunks, request.question, top_k=3)

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
