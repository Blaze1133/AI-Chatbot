from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from typing import List
import os
from app.config import settings

class PDFProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len
        )
    
    def process_pdf(self,file_path:str,document_id:str,filename:str) -> List[Document]:
        """
        Extract text from PDF and split into chunks
        
        Args:
            file_path: Path to the PDF file
            document_id: Unique ID for this document
            filename: Original filename
            
        Returns:
            List of Document objects with text chunks and metadata
        """
        # Load PDF
        loader = PyPDFLoader(file_path)
        pages = loader.load()

        chunks = self.text_splitter.split_documents(pages)

        for i,chunk in enumerate(chunks):
            chunk.metadata.update({
                "document_id":document_id,
                "filename":filename,
                "chunk_index":i
            })
        return chunks
    
    def get_page_count(self,file_path:str)->int:
        """Get the number of pages in a PDF"""
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        return len(pages)
pdf_processor = PDFProcessor()