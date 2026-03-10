from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uuid
import fitz  # PyMuPDF
from typing import Optional, List
from groq import Groq
from langchain_cohere import CohereEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from supabase.client import Client, create_client

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

# Initialize Supabase client and embeddings
supabase_client: Optional[Client] = None
vector_store: Optional[SupabaseVectorStore] = None
embeddings: Optional[CohereEmbeddings] = None

if SUPABASE_URL and SUPABASE_KEY:
    supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
if COHERE_API_KEY:
    embeddings = CohereEmbeddings(
        cohere_api_key=COHERE_API_KEY,
        model="embed-english-light-v3.0"  # Free tier model
    )
    
if supabase_client and embeddings:
    vector_store = SupabaseVectorStore(
        client=supabase_client,
        embedding=embeddings,
        table_name="documents",
        query_name="match_documents"
    )

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


def chunk_documents(pages: List[dict], document_id: str, filename: str) -> List[Document]:
    """Split pages into LangChain Document chunks with metadata."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    
    documents = []
    for page_info in pages:
        page_num = page_info["page"]
        text = page_info["content"]
        
        chunks = text_splitter.split_text(text)
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "document_id": document_id,
                    "filename": filename,
                    "page": page_num,
                    "chunk_index": i,
                }
            )
            documents.append(doc)
    
    return documents


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
        "vector_store_initialized": vector_store is not None,
        "embeddings_initialized": embeddings is not None,
        "supabase_connected": supabase_client is not None
    }

@app.get("/api/test")
async def test():
    return {"message": "Backend API is working!", "deployed": "vercel"}

@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF document and extract its text."""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    if not vector_store:
        raise HTTPException(status_code=503, detail="Vector store not initialized. Please configure SUPABASE_URL, SUPABASE_SERVICE_KEY, and COHERE_API_KEY.")

    document_id = str(uuid.uuid4())

    try:
        file_bytes = await file.read()
        pages = extract_text_from_pdf(file_bytes)

        if not pages:
            raise HTTPException(status_code=400, detail="Could not extract any text from this PDF")

        # Create LangChain documents with metadata
        documents = chunk_documents(pages, document_id, file.filename)
        
        # Add to Supabase vector store
        vector_store.add_documents(documents)
        
        return {
            "message": f"Document uploaded successfully. {len(pages)} pages, {len(documents)} chunks processed.",
            "document_id": document_id,
            "filename": file.filename,
            "pages": len(pages),
            "chunks": len(documents)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document from vector store."""
    if not vector_store or not supabase_client:
        raise HTTPException(status_code=503, detail="Vector store not initialized")
    
    try:
        # Delete from Supabase using metadata filter
        supabase_client.table("documents").delete().eq("metadata->>document_id", document_id).execute()
        return {"message": "Document deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

@app.post("/api/chat/ask")
async def ask_question(request: ChatRequest):
    """Ask a question about an uploaded document using Groq LLM with vector search."""
    if not vector_store:
        raise HTTPException(status_code=503, detail="Vector store not initialized. Please configure SUPABASE_URL, SUPABASE_SERVICE_KEY, and COHERE_API_KEY.")

    try:
        # Semantic search using Supabase vector similarity
        if request.document_id:
            # Search only within specific document
            filter_dict = {"document_id": request.document_id}
            relevant_docs = vector_store.similarity_search(
                request.question,
                k=4,
                filter=filter_dict
            )
        else:
            # Search across all documents
            relevant_docs = vector_store.similarity_search(
                request.question,
                k=4
            )
        
        if not relevant_docs:
            return {
                "answer": "No relevant information found. Please upload a document first.",
                "source_documents": []
            }

        # Build context from relevant chunks
        context_parts = []
        char_count = 0
        filename = relevant_docs[0].metadata.get("filename", "unknown")
        
        for doc in relevant_docs:
            content = doc.page_content
            page = doc.metadata.get("page", 0)
            
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
                "content": doc.page_content[:300] + ("..." if len(doc.page_content) > 300 else ""),
                "page": doc.metadata.get("page", 0),
                "filename": doc.metadata.get("filename", "unknown"),
            }
            for doc in relevant_docs
        ]

        return {
            "answer": answer,
            "source_documents": source_documents,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")
