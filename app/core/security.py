from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.core.config import get_settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    # For MVP, we're not enforcing strict API key checks, but this is a placeholder for it.
    # checking if env var for API key auth is set could be done here.
    return api_key_header
