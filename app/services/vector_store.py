import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from app.core.config import get_settings
import os

settings = get_settings()

class VectorStoreService:
    def __init__(self):
        # Ensure the directory exists
        if not os.path.exists(settings.CHROMA_DB_PATH):
            os.makedirs(settings.CHROMA_DB_PATH)
            
        self.embedding_function = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY,
            model="text-embedding-3-small"
        )
        self.vector_store = Chroma(
            persist_directory=settings.CHROMA_DB_PATH,
            embedding_function=self.embedding_function,
            collection_name="rag_documents"
        )

    def add_documents(self, documents):
        """
        Add documents to the vector store.
        """
        return self.vector_store.add_documents(documents)

    def similarity_search(self, query, k=5):
        """
        Search for documents similar to the query.
        """
        return self.vector_store.similarity_search_with_score(query, k=k)

    def get_retriever(self):
        return self.vector_store.as_retriever()
