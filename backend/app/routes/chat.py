from fastapi import APIRouter,HTTPException
from app.models import QuestionRequest,AnswerResponse,SourceDocument
from app.services.qa_chain import qa_chain_service
from app.services.vector_store import vector_store_service

router = APIRouter(prefix="/api/chat",tags=["chat"])

@router.post("/ask",response_model=AnswerResponse)
async def ask_question(request:QuestionRequest):
    """Ask a question about the documents"""
    
    try:
        # Check if session has expired (30 minutes)
        vector_store_service.check_session_expiry()
        
        # Get answer from QA chain
        result = qa_chain_service.ask(
            question=request.question,
            document_id=request.document_id
        )
        source_docs = []
        for doc in result.get("source_documents", []):
            source_docs.append(SourceDocument(
                content=doc.page_content,
                page=doc.metadata.get("page", 0),
                document_id=doc.metadata.get("document_id", ""),
                filename=doc.metadata.get("filename", "")
            ))
        
        return AnswerResponse(
            answer=result["result"],
            source_documents=source_docs
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

