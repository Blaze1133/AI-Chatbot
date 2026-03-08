from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from typing import List, Optional
from langchain_core.documents import Document
from app.config import settings
import uuid
import tempfile
import shutil
import os
import time
from datetime import datetime, timedelta

class VectorStoreService:
    def __init__(self):
        self._vector_store = None
        self._embeddings = None
        # Create unique session ID for this server instance
        self.session_id = str(uuid.uuid4())
        # Create temporary directory for this session
        self.temp_dir = tempfile.mkdtemp(prefix=f"vector_db_session_{self.session_id}_")
        # Track session creation time
        self.session_created_at = datetime.now()
        # Auto-clear after 30 minutes
        self.session_duration = timedelta(minutes=30)
        print(f" Session-based vector store initialized: {self.session_id}")
        print(f" Temporary directory: {self.temp_dir}")
        print(f" Session will auto-clear after: {self.session_duration}")
    
    @property
    def embeddings(self):
        if self._embeddings is None:
            # Use free HuggingFace embeddings
            self._embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        return self._embeddings
    
    @property
    def vector_store(self):
        if self._vector_store is None:
            self._vector_store = Chroma(
                persist_directory=self.temp_dir,  # Use session-specific temp directory
                embedding_function=self.embeddings,
            )
        return self._vector_store

    def add_documents(self, documents: List[Document]):
        """Add documents to the vector store"""
        self.vector_store.add_documents(documents)
    
    def search(self, query: str, k: int = 4, document_id: Optional[str] = None) -> List[Document]:
        """Search for similar documents

        Args:
            query: The search query
            k: Number of results to return
            document_id: Optional filter by document ID
        """
        
        if document_id:
            filter_dict = {"document_id": document_id}
            return self.vector_store.similarity_search(query, k=k, filter=filter_dict)
        else:
            return self.vector_store.similarity_search(query, k=k)

    def delete_by_document_id(self, document_id: str) -> None:
        """Delete all chunks belonging to a document"""
        # Get all documents with this ID
        results = self.vector_store.get(where={"document_id": document_id})
        if results and results['ids']:
            self.vector_store.delete(ids=results['ids'])
    
    def clear_session(self) -> None:
        """Clear all data from this session and cleanup temporary directory"""
        try:
            # Delete the vector store
            if self._vector_store:
                self._vector_store.delete_collection()
                self._vector_store = None
            
            # Remove temporary directory
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                print(f" Cleared session data: {self.session_id}")
            
            # Reset session
            self.session_id = str(uuid.uuid4())
            self.temp_dir = tempfile.mkdtemp(prefix=f"vector_db_session_{self.session_id}_")
            self.session_created_at = datetime.now()
            print(f" New session created: {self.session_id}")
        except Exception as e:
            print(f" Error clearing session: {e}")
    
    def check_session_expiry(self) -> None:
        """Check if session has expired and clear if needed"""
        if datetime.now() - self.session_created_at > self.session_duration:
            print(f" Session expired: {self.session_id}")
            self.clear_session()
    
    def force_new_session(self) -> None:
        """Force create a new session (clears all data)"""
        print(f" Forcing new session: {self.session_id}")
        self.clear_session()
    
    def __del__(self):
        """Cleanup when service is destroyed"""
        self.clear_session()

# Global session-based vector store service
vector_store_service = VectorStoreService()

# Cleanup function for graceful shutdown
import atexit
def cleanup_on_exit():
    print("🔄 Cleaning up session data on server shutdown...")
    vector_store_service.clear_session()

atexit.register(cleanup_on_exit)