import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.schemas import ChatRequest
from app.services.chat_service import ChatService
from app.providers.chat.registry import ChatProviderRegistry

router = APIRouter()


@router.post("/stream")
async def chat_stream(req: ChatRequest):
    """Streaming chat via SSE."""
    if not ChatProviderRegistry.is_registered(req.provider):
        raise HTTPException(status_code=400,
                            detail=f"Provider '{req.provider}' not available")

    msg_dicts = [{"role": m.role, "content": m.content} for m in req.messages]

    async def event_stream():
        async for chunk in ChatService.stream_chat(
            req.provider, req.model, msg_dicts,
            temperature=req.temperature,
        ):
            if chunk:
                yield f"data: {json.dumps({'token': chunk})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/")
async def chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Non-streaming chat."""
    if not ChatProviderRegistry.is_registered(req.provider):
        raise HTTPException(status_code=400,
                            detail=f"Provider '{req.provider}' not available")

    msg_dicts = [{"role": m.role, "content": m.content} for m in req.messages]

    content, conv_id = await ChatService.chat(
        req.provider, req.model, msg_dicts,
        db=db, conversation_id=req.conversation_id,
        temperature=req.temperature,
    )
    return {"content": content, "conversation_id": conv_id}


@router.get("/conversations")
async def list_conversations(db: AsyncSession = Depends(get_db)):
    conversations = await ChatService.list_conversations(db)
    return {"conversations": conversations}


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str,
                           db: AsyncSession = Depends(get_db)):
    conv = await ChatService.get_conversation(db, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@router.post("/conversations")
async def create_conversation(
    provider: str = "openai",
    model: str = "",
    title: str = "New Chat",
    db: AsyncSession = Depends(get_db),
):
    conv = await ChatService.create_conversation(db, provider, model, title)
    return {"id": conv.id, "title": conv.title}
