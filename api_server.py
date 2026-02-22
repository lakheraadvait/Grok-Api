from fastapi import FastAPI, HTTPException
from urllib.parse import urlparse, ParseResult
from pydantic import BaseModel
from typing import Optional
from core import Grok
from uvicorn import run


app = FastAPI()


# -----------------------------
# Request Model
# -----------------------------

class ConversationRequest(BaseModel):
    proxy: Optional[str] = None
    message: str
    model: str = "grok-3-auto"
    extra_data: Optional[dict] = None


# -----------------------------
# Proxy Formatter
# -----------------------------

def format_proxy(proxy: str) -> str:

    if not proxy.startswith(("http://", "https://")):
        proxy = "http://" + proxy

    parsed: ParseResult = urlparse(proxy)

    if parsed.scheme not in ("http", "https"):
        raise ValueError("Not http/https scheme")

    if not parsed.hostname or not parsed.port:
        raise ValueError("No url and port")

    if parsed.username and parsed.password:
        return f"http://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port}"

    return f"http://{parsed.hostname}:{parsed.port}"


# -----------------------------
# API Endpoint
# -----------------------------

@app.post("/ask")
async def create_conversation(request: ConversationRequest):

    if not request.message:
        raise HTTPException(
            status_code=400,
            detail="Message is required"
        )

    proxy = None

    try:
        if request.proxy:
            proxy = format_proxy(request.proxy)

        answer: dict = Grok(
            request.model,
            proxy
        ).start_convo(
            request.message,
            request.extra_data
        )

        return {
            "status": "success",
            **answer
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


# -----------------------------
# Run Server
# -----------------------------

if __name__ == "__main__":
    run(
        "api_server:app",
        host="0.0.0.0",
        port=6969,
        workers=1
    )
