from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.azure_client import get_chat_completion

app = FastAPI(title="basic-ai-agent")


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.get("/readyz")
def readyz() -> dict:
    return {"status": "ready"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="message must not be empty")
    reply = get_chat_completion(request.message)
    return ChatResponse(reply=reply)
