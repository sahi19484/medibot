from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class User(db.Model):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    plan: Mapped[str] = mapped_column(String(20), default='basic', nullable=False)
    language: Mapped[str] = mapped_column(String(5), default='en', nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    chat_sessions: Mapped[List["ChatSession"]] = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    daily_usage: Mapped[List["DailyUsage"]] = relationship("DailyUsage", back_populates="user", cascade="all, delete-orphan")

class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    session_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    bot_response_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="chat_sessions")
    messages: Mapped[List["ChatMessage"]] = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey('chat_sessions.id'), nullable=False)
    message_type: Mapped[str] = mapped_column(String(10), nullable=False)  # 'user' or 'bot'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    disease: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    medicines: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="messages")

class DailyUsage(db.Model):
    __tablename__ = 'daily_usage'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    date: Mapped[str] = mapped_column(String(10), nullable=False)  # YYYY-MM-DD format
    chat_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="daily_usage")
    
    # Unique constraint for user_id and date combination
    __table_args__ = (db.UniqueConstraint('user_id', 'date', name='unique_user_date'),)

class Disease(db.Model):
    __tablename__ = 'diseases'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    symptoms: Mapped[list] = mapped_column(JSON, nullable=False)
    medicines: Mapped[list] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SubscriptionPlan(db.Model):
    __tablename__ = 'subscription_plans'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plan_key: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    price: Mapped[str] = mapped_column(String(20), nullable=False)
    max_chats_per_day: Mapped[int] = mapped_column(Integer, nullable=False)
    max_bot_responses_per_chat: Mapped[int] = mapped_column(Integer, nullable=False)
    medicine_images: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    chat_history: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    voice_chat: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    available_languages: Mapped[list] = mapped_column(JSON, nullable=False)
    layout: Mapped[str] = mapped_column(String(20), default='standard', nullable=False)
    features: Mapped[list] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)