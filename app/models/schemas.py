from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class UploadResponse(BaseModel):
    status: str
    document_id: str
    chunks_processed: int
    message: str

class QueryRequest(BaseModel):
    question: str
    top_k: int = 5

class Source(BaseModel):
    content: str
    document: str
    page: Optional[int] = None
    score: Optional[float] = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[Source]
    agent_steps: List[str] = []
