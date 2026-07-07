from sqlalchemy import Column, DateTime
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel, Text
from datetime import datetime, timezone

class Users(SQLModel, table = True):
    __tablename__ = "users"
    
    user_id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str

    conversations: List['Conversation'] = Relationship(back_populates='user')
    notes: List['Note'] = Relationship(back_populates='user')
    
class Conversation(SQLModel, table = True):
    __tablename__ = "conversations"
    
    conversation_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key='users.user_id')
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=lambda: datetime.now(timezone.utc),
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    user: Users = Relationship(back_populates='conversations')
    messages: List['Message'] = Relationship(back_populates='conversations')
    tool_calls: List["ToolCall"] = Relationship(back_populates="conversation")
    
class Message(SQLModel, table = True):
    __tablename__ = "messages"
    
    message_id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key='conversations.conversation_id')
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=lambda: datetime.now(timezone.utc),
    )
    role: str
    content: str

    conversations: Optional[Conversation] = Relationship(back_populates='messages')

class Note(SQLModel, table=True):
    __tablename__ = "notes"

    note_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key='users.user_id')
    title: str
    content: str
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=lambda: datetime.now(timezone.utc),
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    user: Users = Relationship(back_populates='notes')

class ToolCall(SQLModel, table=True):
    __tablename__ = "tool_calls"
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key='conversations.conversation_id', index=True)
    tool_name: str = Field(index=True)
    tool_input: str = Field(sa_column=Column(Text, nullable=False))
    tool_output: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    status: str = Field(default="success", index=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=lambda: datetime.now(timezone.utc),
    )

    conversation: Optional[Conversation] = Relationship(back_populates='tool_calls')