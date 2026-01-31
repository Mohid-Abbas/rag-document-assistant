import os
from typing import List
from fastapi import UploadFile
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
import shutil
import tempfile
from app.services.vector_store import VectorStoreService

class RAGPipeline:
    def __init__(self):
        self.vector_store_service = VectorStoreService()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

    async def process_document(self, file: UploadFile) -> str:
        # Create a temporary file to store the uploaded content
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp_file:
                shutil.copyfileobj(file.file, tmp_file)
                tmp_path = tmp_file.name

            # Load document based on file type
            if file.filename.endswith(".pdf"):
                loader = PyPDFLoader(tmp_path)
            else:
                loader = TextLoader(tmp_path)
            
            documents = loader.load()
            
            # Split documents
            chunks = self.text_splitter.split_documents(documents)
            
            # Add to vector store
            ids = self.vector_store_service.add_documents(chunks)
            
            return len(ids)
            
        finally:
            if 'tmp_path' in locals():
                os.remove(tmp_path)

    def retrieve(self, query: str, k: int = 5):
        return self.vector_store_service.similarity_search(query, k)
