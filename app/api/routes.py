from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.models.schemas import UploadResponse, QueryRequest, QueryResponse, Source
from app.services.rag_pipeline import RAGPipeline
from app.services.agent import AgentService
from app.core.security import get_api_key

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    api_key: str = Depends(get_api_key)
):
    try:
        pipeline = RAGPipeline()
        num_chunks = await pipeline.process_document(file)
        
        return UploadResponse(
            status="success",
            document_id=file.filename,
            chunks_processed=num_chunks,
            message="Document processed and embedded successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=QueryResponse)
async def query_knowledge_base(
    request: QueryRequest,
    api_key: str = Depends(get_api_key)
):
    try:
        # Retrieve context
        pipeline = RAGPipeline()
        results = pipeline.retrieve(request.question, k=request.top_k)
        
        sources = [
            Source(
                content=doc.page_content,
                document=doc.metadata.get("source", "unknown"),
                page=doc.metadata.get("page"),
                score=score
            ) for doc, score in results
        ]

        # Generate answer using Agent
        agent = AgentService()
        answer = await agent.process_query(request.question)
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            agent_steps=["Retrieved relevant chunks", "Generated response using Agent"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
