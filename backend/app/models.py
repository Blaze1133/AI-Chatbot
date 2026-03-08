from pydantic import BaseModel
from typing import List,Optional
from datetime import datetime

class Base(BaseModel):
    pass

class DocumentUploadResponse(Base):
    document_id: str
    filename: str
    status: str
    message: str

class QuestionRequest(Base):
    question:str
    document_id:Optional[str] = None

class SourceDocument(Base):
    content:str
    page:int
    document_id:str
    filename:str

class AnswerResponse(Base):
    answer:str
    source_documents: List[SourceDocument]

class DocumentInfo(Base):
    document_id:str
    filename:str
    page_count:int
    upload_date:str