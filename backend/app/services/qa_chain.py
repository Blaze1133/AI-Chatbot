from langchain_groq import ChatGroq
from langchain_classic.chains import RetrievalQA
from app.config import settings
from langchain_core.prompts import PromptTemplate
from app.services.vector_store import vector_store_service

class QAChainService:
    def __init__(self):
        self._llm = None
        self._prompt = None
        self._qa_chain = None
    
    @property
    def llm(self):
        if self._llm is None:
            self._llm = ChatGroq(
                groq_api_key=settings.GROQ_API_KEY,
                model_name=settings.MODEL_NAME,
                temperature=settings.TEMPERATURE
            )
        return self._llm
    
    @property
    def prompt(self):
        if self._prompt is None:
            template = """Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Keep the answer concise and relevant.
Context: {context}
Question: {question}
Answer:"""
            self._prompt = PromptTemplate(template=template,input_variables=["context", "question"])
        return self._prompt
    
    @property
    def qa_chain(self):
        if self._qa_chain is None:
            self._qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=vector_store_service.vector_store.as_retriever(search_kwargs={"k": 3}),
                return_source_documents=True,
                chain_type_kwargs={"prompt": self.prompt}
            )
        return self._qa_chain
    
    def ask(self,question:str,document_id:str=None):
        """
        Ask a question and get an AI-generated answer
        
        Args:
            question: The user's question
            document_id: Optional document ID to filter search
            
        Returns:
            dict with 'result' (answer) and 'source_documents' (sources)
        """

        if document_id:
            retriever = vector_store_service.vector_store.as_retriever(
                search_kwargs={"k": 4, "filter": {"document_id": document_id}}
            )
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True,
                chain_type_kwargs={"prompt": self.prompt}
            )
            return qa_chain({"query": question})
        else:
            # Search all documents
            return self.qa_chain({"query": question})
qa_chain_service = QAChainService()