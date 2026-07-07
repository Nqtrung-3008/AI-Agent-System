from typing import List, Optional
from sqlmodel import SQLModel
from datetime import datetime

class UserBase(SQLModel):
    username: str
    
class UserRegister(UserBase):
    username: str
    password: str
    
class UserPublic(UserBase):
    user_id: int

class UserLogin(UserBase):
    username: str
    password: str

class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"
    
class ConversationBase(SQLModel):
    pass
    
class ConversationCreate(ConversationBase):
    pass
    
class ConversationPublic(ConversationBase):
    conversation_id: int
    created_at: datetime
    
class ConversationDelete(SQLModel):
      deleted: bool

class MessageBase(SQLModel):
    content: str
    role: str
    
class MessageCreate(MessageBase):
    conversation_id: int
    
class MessagePublic(MessageBase):
    message_id: int
    conversation_id: int
    created_at: datetime
    
class ChatRequest(SQLModel):
    content: str
    conversation_id: int

class ChatResponse(SQLModel):
    answer: str

class NoteBase(SQLModel):
    title: str
    content: str

class NoteCreate(NoteBase):
    pass    

class NotePublic(NoteBase):
    note_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

class NoteDelete(SQLModel):
      deleted: bool

class ToolCallPublic(SQLModel):
    id: int
    conversation_id: int
    tool_name: str
    tool_input: str
    tool_output: Optional[str] = None
    status: str
    created_at: datetime

class ToolCallCreate(SQLModel):
    conversation_id: int
    tool_name: str
    tool_input: str
    tool_output: Optional[str] = None
    status: str = "success"
