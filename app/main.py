from fastapi import FastAPI
from app.api.routes import router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(router, prefix="")

@app.get("/")
async def root():
    return {"message": "Intelligent Document RAG Assistant API is running"}
