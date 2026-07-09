from typing import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models import Conversation, Message
from app.providers.chat.registry import ChatProviderRegistry


class ChatService:
    @staticmethod
    async def chat(
        provider_name: str,
        model: str,
        messages: list[dict],
        db: AsyncSession | None = None,
        conversation_id: str | None = None,
        **kwargs,
    ) -> tuple[str, str]:
        """Non-streaming chat. Returns (content, conversation_id)."""
        provider = ChatProviderRegistry.get(provider_name)
        model = model or provider.get_available_models()[0].id

        content = await provider.chat(messages, model=model, **kwargs)

        if db and conversation_id:
            await ChatService._save_messages(db, conversation_id, messages, content)

        return content, conversation_id or ""

    @staticmethod
    async def stream_chat(
        provider_name: str,
        model: str,
        messages: list[dict],
        **kwargs,
    ) -> AsyncIterator[str]:
        """Streaming chat. Yields content chunks."""
        provider = ChatProviderRegistry.get(provider_name)
        model = model or provider.get_available_models()[0].id

        async for chunk in provider.chat_stream(messages, model=model, **kwargs):
            yield chunk

    @staticmethod
    async def create_conversation(
        db: AsyncSession,
        provider: str,
        model: str,
        title: str = "New Chat",
    ) -> Conversation:
        conv = Conversation(provider=provider, model=model, title=title)
        db.add(conv)
        await db.commit()
        await db.refresh(conv)
        return conv

    @staticmethod
    async def _save_messages(
        db: AsyncSession,
        conversation_id: str,
        messages: list[dict],
        assistant_content: str,
    ):
        for m in messages:
            if m["role"] in ("user", "system"):
                msg = Message(conversation_id=conversation_id, role=m["role"],
                              content=m["content"])
                db.add(msg)
        msg = Message(conversation_id=conversation_id, role="assistant",
                      content=assistant_content)
        db.add(msg)
        # Update conversation title from first user message
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        result = await db.execute(stmt)
        conv = result.scalar_one_or_none()
        if conv:
            first_user = next((m["content"] for m in messages
                               if m["role"] == "user"), None)
            if first_user and conv.title == "New Chat":
                conv.title = first_user[:80]
        await db.commit()

    @staticmethod
    async def list_conversations(db: AsyncSession) -> list[dict]:
        stmt = select(
            Conversation.id,
            Conversation.title,
            Conversation.provider,
            Conversation.model,
            Conversation.created_at,
            func.count(Message.id).label("message_count"),
        ).outerjoin(
            Message, Message.conversation_id == Conversation.id
        ).group_by(
            Conversation.id
        ).order_by(Conversation.updated_at.desc())

        result = await db.execute(stmt)
        rows = result.all()
        return [
            {
                "id": r.id,
                "title": r.title,
                "provider": r.provider,
                "model": r.model,
                "created_at": r.created_at.isoformat(),
                "message_count": r.message_count,
            }
            for r in rows
        ]

    @staticmethod
    async def get_conversation(db: AsyncSession, conv_id: str) -> dict | None:
        stmt = select(Conversation).where(Conversation.id == conv_id)
        result = await db.execute(stmt)
        conv = result.scalar_one_or_none()
        if not conv:
            return None
        return {
            "id": conv.id,
            "title": conv.title,
            "provider": conv.provider,
            "model": conv.model,
            "created_at": conv.created_at.isoformat(),
            "messages": [{"role": m.role, "content": m.content}
                         for m in conv.messages],
        }
