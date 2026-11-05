import os
import secrets

from fastapi import HTTPException, Request
from fastapi.security import APIKeyHeader
from fastapi import Depends

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(
    request: Request,
    supplied_key: str | None = Depends(api_key_header),
):
    if request.url.path == "/health":
        return

    expected_key = os.getenv("NOTES_API_KEY", "")

    if not expected_key:
        if os.getenv("NOTES_BACKEND", "memory") == "memory":
            return
        raise HTTPException(status_code=503, detail="API key non configurata")

    if not supplied_key or not secrets.compare_digest(
        supplied_key.encode(), expected_key.encode()
    ):
        raise HTTPException(status_code=401, detail="API key non valida")
