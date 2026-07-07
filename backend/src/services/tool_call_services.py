from typing import List
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.src.models.models import ToolCall, Conversation
from backend.src.schemas.schemas import ToolCallCreate

async def create_tool_call(tool_call_data: ToolCallCreate,session: AsyncSession) -> ToolCall:
    db_tool_call = ToolCall.model_validate(tool_call_data)
    session.add(db_tool_call)
    await session.flush()
    await session.refresh(db_tool_call)
    return db_tool_call

async def get_tool_calls_by_conversation(conversation_id: int, user_id: int, session: AsyncSession) -> List[ToolCall]:
    statement = select(ToolCall).join(Conversation).where(ToolCall.conversation_id == conversation_id, 
                                                          Conversation.user_id == user_id,
                                                          Conversation.deleted_at.is_(None)).order_by(ToolCall.created_at)
    result = await session.exec(statement)
    return result.all()