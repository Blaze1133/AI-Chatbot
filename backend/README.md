# AI Document Assistant - Backend

A FastAPI-based backend service that enables intelligent question-answering over PDF documents using LangChain, Groq LLM, and ChromaDB vector storage.

## Tech Stack

- **FastAPI** - Web framework
- **LangChain** - LLM orchestration
- **Groq** - LLM provider (llama-3.3-70b-versatile)
- **ChromaDB** - Vector database
- **HuggingFace Embeddings** - Text embeddings
- **PyPDF** - PDF processing

## Prerequisites

- Python 3.8+
- Groq API key ([Get one here](https://console.groq.com))

## Installation

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the backend directory:
```env
GROQ_API_KEY=your_groq_api_key_here
MODEL_NAME=llama-3.3-70b-versatile
TEMPERATURE=0.7
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
UPLOAD_DIR=uploads
VECTOR_DB_PATH=vector_db
```

## Running the Server

Start the development server:
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Upload Document
```http
POST /api/documents/upload
Content-Type: multipart/form-data

file: <PDF file>
```

**Response:**
```json
{
  "document_id": "uuid-string",
  "filename": "document.pdf",
  "status": "success",
  "message": "Document uploaded successfully. X pages processed."
}
```

### Delete Document
```http
DELETE /api/documents/{document_id}
```

**Response:**
```json
{
  "status": "success",
  "message": "Document deleted successfully"
}
```

### Ask Question
```http
POST /api/chat/ask
Content-Type: application/json

{
  "question": "What are the main findings?",
  "document_id": "uuid-string" // optional
}
```

**Response:**
```json
{
  "answer": "The main findings are...",
  "source_documents": [
    {
      "content": "excerpt from document",
      "page": 5,
      "document_id": "uuid-string",
      "filename": "document.pdf"
    }
  ]
}
```

### Health Check
```http
GET /health
```

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── routes/
│   │   ├── documents.py     # Document upload/delete endpoints
│   │   └── chat.py          # Question-answering endpoint
│   └── services/
│       ├── pdf_processor.py # PDF text extraction
│       ├── vector_store.py  # ChromaDB operations
│       └── qa_chain.py      # LangChain QA chain
├── uploads/                 # Uploaded PDF files
├── vector_db/              # ChromaDB storage
├── requirements.txt
└── .env
```

## How It Works

1. **Document Upload**: PDFs are uploaded and split into chunks using RecursiveCharacterTextSplitter
2. **Embedding**: Text chunks are converted to embeddings using HuggingFace models
3. **Storage**: Embeddings are stored in ChromaDB with metadata (filename, page, document_id)
4. **Retrieval**: When a question is asked, relevant chunks are retrieved using similarity search
5. **Generation**: Groq LLM generates an answer based on the retrieved context

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq API key | Required |
| `MODEL_NAME` | Groq model to use | llama-3.3-70b-versatile |
| `TEMPERATURE` | LLM temperature (0-1) | 0.7 |
| `CHUNK_SIZE` | Text chunk size | 1000 |
| `CHUNK_OVERLAP` | Overlap between chunks | 200 |
| `UPLOAD_DIR` | Directory for uploaded files | uploads |
| `VECTOR_DB_PATH` | ChromaDB storage path | vector_db |

### Chunking Strategy

The system uses RecursiveCharacterTextSplitter with:
- Chunk size: 1000 characters
- Overlap: 200 characters
- This ensures context continuity while maintaining manageable chunk sizes

## Troubleshooting

### "Module not found" errors
Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### ChromaDB errors
Delete the `vector_db` directory and restart:
```bash
rm -rf vector_db
```

### Groq API errors
- Verify your API key is correct in `.env`
- Check your Groq account has available credits
- Ensure you're using a valid model name

### CORS errors
The backend is configured to allow requests from `http://localhost:3000` and `http://localhost:3002`. Update `app/main.py` if your frontend runs on a different port.

## Development

### Running Tests
```bash
# Test Groq API connection
python test_groq.py
```

### Lazy Initialization
The vector store and QA chain use lazy initialization to improve startup time. They're only initialized when first accessed.

## Notes

- PDF files are stored in the `uploads/` directory
- Vector embeddings are persisted in `vector_db/`
- Each document is assigned a unique UUID
- The system supports multiple documents simultaneously
- Questions can be asked across all documents or filtered by document_id

## License

MIT
