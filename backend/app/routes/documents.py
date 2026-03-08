from fastapi import APIRouter, UploadFile,File,HTTPException
from app.models import DocumentUploadResponse,DocumentInfo
from app.services.pdf_processor import pdf_processor
from app.services.vector_store import vector_store_service
from app.config import settings
import uuid
import os
from datetime import datetime
from typing import List

router = APIRouter(prefix="/api/documents",tags=["documents"])

@router.post("/upload",response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """UPLOAD PDF DOC"""
    
    # Check if session has expired (30 minutes)
    vector_store_service.check_session_expiry()
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    document_id = str(uuid.uuid4())
    file_path = os.path.join(settings.UPLOAD_DIR, f"{document_id}.pdf")

    try:
        with open(file_path,"wb") as f:
            content = await file.read()
            f.write(content)
        
        chunks = pdf_processor.process_pdf(file_path,document_id,file.filename)
        vector_store_service.add_documents(chunks)
        page_count = pdf_processor.get_page_count(file_path)

        return DocumentUploadResponse(
            document_id=document_id,
            filename=file.filename,
            status="success",
            message=f"Document uploaded and processed successfully. {page_count} pages processed."
        )
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@router.delete("/{document_id}")
async def delete_document(document_id:str):
    """Delete a document"""
    try:
        vector_store_service.delete_by_document_id(document_id)
        file_path = os.path.join(settings.UPLOAD_DIR, f"{document_id}.pdf")
        if os.path.exists(file_path):
            os.remove(file_path)
        return {"status":"success","message": "Document deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")