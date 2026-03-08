# AI Document Assistant - Backend Detailed Flow & Architecture

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Data Flow](#data-flow)
4. [Core Components Deep Dive](#core-components-deep-dive)
5. [Implementation Details](#implementation-details)
6. [Key Technologies & Concepts](#key-technologies--concepts)
7. [Interview Preparation Points](#interview-preparation-points)
8. [Code Walkthrough](#code-walkthrough)

## Project Overview

The AI Document Assistant is a sophisticated question-answering system that allows users to upload PDF documents and ask natural language questions about their content. The backend processes these documents, creates searchable vector embeddings, and uses Large Language Models (LLMs) to provide accurate, source-cited answers.

### Key Features
- **Document Processing**: PDF text extraction and intelligent chunking
- **Vector Storage**: Semantic search using ChromaDB
- **LLM Integration**: Groq's Llama model for intelligent responses
- **Source Citation**: Every answer includes exact document references
- **Multi-document Support**: Query across multiple documents simultaneously

## System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI        │    │   External      │
│   (Next.js)     │◄──►│   Backend        │◄──►│   Services      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Local Storage  │
                    │   - ChromaDB     │
                    │   - PDF Files    │
                    └──────────────────┘
```

### Architecture Components

1. **API Layer** (FastAPI)
   - RESTful endpoints for document management
   - Request validation and error handling
   - CORS configuration for frontend communication

2. **Processing Layer** (Services)
   - PDF text extraction
   - Text chunking and embedding
   - Vector storage operations
   - LLM integration

3. **Storage Layer**
   - ChromaDB for vector embeddings
   - File system for PDF storage
   - Persistent data across sessions

## Data Flow

### 1. Document Upload Flow

```
User Uploads PDF
       │
       ▼
FastAPI Endpoint (/api/documents/upload)
       │
       ▼
File Validation (PDF only)
       │
       ▼
PDFProcessor.extract_text()
       │
       ▼
TextSplitter.split_documents()
       │
       ▼
Embedding Generation (HuggingFace)
       │
       ▼
ChromaDB Storage
       │
       ▼
Success Response to User
```

### 2. Question-Answering Flow

```
User Asks Question
       │
       ▼
FastAPI Endpoint (/api/chat/ask)
       │
       ▼
VectorStoreService.search()
       │
       ▼
Retrieve Relevant Chunks
       │
       ▼
QAChainService.ask()
       │
       ▼
LLM Generates Answer
       │
       ▼
Format Response with Sources
       │
       ▼
Return to User
```

## Core Components Deep Dive

### 1. Configuration Management (`app/config.py`)

**Purpose**: Centralized configuration using Pydantic for type safety and validation.

```python
class Settings(BaseSettings):
    # OpenAI Configuration (legacy name, uses Groq)
    OPENAI_API_KEY: str  # Groq API key
    
    # Paths
    UPLOAD_DIR: str = "uploads"
    VECTOR_DB_PATH: str = "vector_db"
    
    # Text Processing
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # Model Configuration
    MODEL_NAME: str = "llama-3.3-70b-versatile"
    TEMPERATURE: float = 0.7
```

**Key Concepts**:
- **Environment Variables**: Securely store sensitive data
- **Default Values**: Provide sensible defaults for development
- **Type Hints**: Ensure data type safety
- **Pydantic Validation**: Automatic validation and error handling

### 2. PDF Processing (`app/services/pdf_processor.py`)

**Purpose**: Extract text from PDFs and split into manageable chunks.

```python
class PDFProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,      # 1000 chars
            chunk_overlap=settings.CHUNK_OVERLAP, # 200 chars
            length_function=len,
        )
```

**Key Concepts**:
- **RecursiveCharacterTextSplitter**: Intelligently splits text while preserving context
- **Chunk Overlap**: Ensures no information is lost at chunk boundaries
- **Metadata Enrichment**: Each chunk gets document_id, filename, page info

**Processing Steps**:
1. Load PDF using PyPDFLoader
2. Split pages into text chunks
3. Add metadata to each chunk
4. Return Document objects for vector storage

### 3. Vector Storage (`app/services/vector_store.py`)

**Purpose**: Manage document embeddings and similarity search using ChromaDB.

```python
class VectorStoreService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()  # Uses HuggingFace in practice
        self.vector_store = None  # Lazy initialization
    
    def add_documents(self, documents: List[Document]):
        """Add documents to vector store"""
        if not self.vector_store:
            self._initialize_vector_store()
        
        self.vector_store.add_documents(documents)
    
    def search(self, query: str, document_id: str = None):
        """Search for relevant documents"""
        if not self.vector_store:
            self._initialize_vector_store()
        
        # Filter by document_id if specified
        search_kwargs = {"k": 4}
        if document_id:
            search_kwargs["filter"] = {"document_id": document_id}
        
        return self.vector_store.similarity_search(query, **search_kwargs)
```

**Key Concepts**:
- **Lazy Initialization**: Vector store created only when needed
- **Embeddings**: Text converted to vectors for semantic search
- **Similarity Search**: Find most relevant chunks based on vector similarity
- **Metadata Filtering**: Search within specific documents

### 4. QA Chain Service (`app/services/qa_chain.py`)

**Purpose**: Orchestrate LLM calls for question answering using retrieved context.

```python
class QAChainService:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.MODEL_NAME,
            temperature=settings.TEMPERATURE
        )
        
        self.prompt = PromptTemplate(
            template="""Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Keep the answer concise and relevant.

Context: {context}
Question: {question}
Answer:""",
            input_variables=["context", "question"]
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=vector_store_service.vector_store.as_retriever(),
            return_source_documents=True,
            chain_type_kwargs={"prompt": self.prompt}
        )
```

**Key Concepts**:
- **RetrievalQA**: LangChain's retrieval-augmented generation chain
- **Prompt Engineering**: Structured prompts for consistent responses
- **Stuff Chain Type**: All retrieved context stuffed into single prompt
- **Source Documents**: Returns original chunks for citation

### 5. API Routes (`app/routes/documents.py` & `app/routes/chat.py`)

**Purpose**: HTTP endpoints for frontend communication.

**Document Upload Endpoint**:
```python
@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    # 1. Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # 2. Generate unique document ID
    document_id = str(uuid.uuid4())
    
    # 3. Save file temporarily
    file_path = os.path.join(settings.UPLOAD_DIR, f"{document_id}.pdf")
    
    # 4. Process PDF
    chunks = pdf_processor.process_pdf(file_path, document_id, file.filename)
    
    # 5. Add to vector store
    vector_store_service.add_documents(chunks)
    
    # 6. Return success response
    return DocumentUploadResponse(
        document_id=document_id,
        filename=file.filename,
        status="success",
        message=f"Document uploaded successfully. {page_count} pages processed."
    )
```

**Chat Endpoint**:
```python
@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    # 1. Get answer from QA chain
    result = qa_chain_service.ask(
        question=request.question,
        document_id=request.document_id
    )
    
    # 2. Format source documents
    source_docs = []
    for doc in result.get("source_documents", []):
        source_docs.append(SourceDocument(
            content=doc.page_content,
            page=doc.metadata.get("page", 0),
            document_id=doc.metadata.get("document_id", ""),
            filename=doc.metadata.get("filename", "")
        ))
    
    # 3. Return formatted response
    return AnswerResponse(
        answer=result["result"],
        source_documents=source_docs
    )
```

## Implementation Details

### Error Handling Strategy

1. **Validation Errors**: Pydantic models validate input data
2. **File Errors**: Check file types, sizes, and corruption
3. **API Errors**: HTTPException with appropriate status codes
4. **Service Errors**: Try-catch blocks with cleanup

### Performance Optimizations

1. **Lazy Initialization**: Services created only when needed
2. **Chunking Strategy**: Optimal chunk size for context vs performance
3. **Vector Indexing**: ChromaDB provides efficient similarity search
4. **Connection Pooling**: Reuse embeddings and LLM connections

### Security Considerations

1. **API Keys**: Environment variables, never hardcoded
2. **File Uploads**: Type validation, size limits
3. **Input Sanitization**: Prompt injection prevention
4. **CORS**: Restricted to frontend domains

## Key Technologies & Concepts

### 1. FastAPI
- Modern Python web framework
- Automatic API documentation
- Type hints for validation
- Async support for performance

### 2. LangChain
- LLM orchestration framework
- Retrieval-augmented generation (RAG)
- Chain composition
- Prompt templates

### 3. ChromaDB
- Vector database for embeddings
- Semantic similarity search
- Metadata filtering
- Persistent storage

### 4. Embeddings
- Text-to-vector conversion
- Semantic similarity
- HuggingFace models
- Dimension reduction

### 5. RAG (Retrieval-Augmented Generation)
- Retrieve relevant context
- Generate responses based on context
- Source citation
- Reduced hallucination

## Interview Preparation Points

### Technical Questions

**Q: How does the system handle large documents?**
A: Documents are split into 1000-character chunks with 200-character overlap, ensuring no context loss while maintaining manageable sizes for processing.

**Q: Why use ChromaDB instead of a traditional database?**
A: ChromaDB specializes in vector similarity search, which is essential for finding semantically relevant text chunks. Traditional databases are optimized for exact matches, not semantic similarity.

**Q: How do you ensure answers are accurate and not hallucinated?**
A: The system uses Retrieval-Augmented Generation (RAG). The LLM only sees relevant document chunks and is instructed to answer based on the provided context, with explicit instructions to say "I don't know" if the answer isn't in the context.

**Q: What's the purpose of chunk overlap?**
A: Overlap ensures that concepts spanning chunk boundaries aren't lost. A 200-character overlap provides context continuity while preventing excessive redundancy.

**Q: How do you handle multiple documents?**
A: Each document gets a unique UUID stored as metadata. The system can search across all documents or filter by specific document_id using ChromaDB's metadata filtering.

### Architecture Questions

**Q: Why use lazy initialization for services?**
A: Improves startup time by avoiding expensive operations (like loading embeddings or connecting to ChromaDB) until they're actually needed. This is crucial for containerized deployments.

**Q: How would you scale this system?**
A: 
- Horizontal scaling: Multiple API instances behind a load balancer
- Vector database: Use managed ChromaDB or Pinecone for larger datasets
- Caching: Redis for frequent queries
- Async processing: Queue system for document processing

**Q: How do you handle concurrent uploads?**
A: Each document gets a unique UUID, and ChromaDB handles concurrent writes. File operations are atomic, and the system maintains thread safety through proper service design.

### Code-Specific Questions

**Q: Explain the PromptTemplate design.**
A: The template uses {context} and {question} placeholders, instructing the LLM to use only the provided context. This prevents hallucination and ensures answers are grounded in the documents.

**Q: What's RetrievalQA and why use "stuff" chain type?**
A: RetrievalQA is LangChain's RAG implementation. "Stuff" means all retrieved chunks are stuffed into a single prompt, which is optimal for our use case where we want comprehensive answers.

**Q: How does metadata work in ChromaDB?**
A: Each chunk stores document_id, filename, page, and chunk_index. This enables filtering searches by document and provides source citations in responses.

## Code Walkthrough

### Complete Request Flow

1. **Upload Request**:
   ```python
   # FastAPI receives multipart/form-data
   file: UploadFile = File(...)
   
   # Validation
   if not file.filename.endswith('.pdf'):
       raise HTTPException(status_code=400)
   
   # Unique ID generation
   document_id = str(uuid.uuid4())
   
   # File storage
   file_path = os.path.join(settings.UPLOAD_DIR, f"{document_id}.pdf")
   ```

2. **Processing Pipeline**:
   ```python
   # PDF processing
   chunks = pdf_processor.process_pdf(file_path, document_id, file.filename)
   
   # Each chunk has metadata:
   # {
   #   "document_id": "uuid",
   #   "filename": "document.pdf",
   #   "page": 5,
   #   "chunk_index": 3
   # }
   
   # Vector storage
   vector_store_service.add_documents(chunks)
   ```

3. **Query Processing**:
   ```python
   # Search for relevant chunks
   relevant_docs = vector_store_service.search(
       query="What are the main findings?",
       document_id="uuid"  # optional filter
   )
   
   # Generate answer
   result = qa_chain_service.ask(
       question="What are the main findings?",
       document_id="uuid"
   )
   
   # Format response with sources
   return AnswerResponse(
       answer=result["result"],
       source_documents=[...formatted_sources...]
   )
   ```

### Error Handling Example

```python
try:
    # Process document
    chunks = pdf_processor.process_pdf(file_path, document_id, filename)
    vector_store_service.add_documents(chunks)
    
except Exception as e:
    # Cleanup on failure
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Raise user-friendly error
    raise HTTPException(
        status_code=500,
        detail=f"Error processing document: {str(e)}"
    )
```

## Future Enhancements

1. **Document Types**: Support for Word, TXT, and other formats
2. **Streaming**: Real-time processing for large documents
3. **Caching**: Redis for query result caching
4. **Analytics**: Track query patterns and document usage
5. **Advanced RAG**: Multi-hop reasoning and document synthesis
6. **Security**: Document access control and user authentication

This detailed documentation should serve as a comprehensive reference for understanding the system architecture, implementation details, and prepare for technical interviews.
