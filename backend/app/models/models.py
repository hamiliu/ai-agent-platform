import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), default="New Chat")
    provider = Column(String(50))
    model = Column(String(100))
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    messages = relationship("Message", back_populates="conversation",
                            cascade="all, delete-orphan", order_by="Message.created_at")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id"))
    role = Column(String(20))       # user / assistant / system
    content = Column(Text)
    created_at = Column(DateTime, default=_utcnow)

    conversation = relationship("Conversation", back_populates="messages")


class GenerationRecord(Base):
    """Records for image/voice generation history."""
    __tablename__ = "generation_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    gen_type = Column(String(20))   # text-to-image / image-to-image / voice-clone
    provider = Column(String(50))
    model = Column(String(100))
    prompt = Column(Text)
    input_file_path = Column(String(500), nullable=True)
    output_file_path = Column(String(500))
    created_at = Column(DateTime, default=_utcnow)
