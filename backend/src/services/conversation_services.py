from typing import List
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.src.models.models import Conversation
from backend.src.schemas.schemas import ConversationCreate
from datetime import datetime, timezone

async def create_conversation(conversation_data: ConversationCreate, user_id: int,session: AsyncSession) -> Conversation:
    conversation_dict = conversation_data.model_dump()
    db_conversation = Conversation(**conversation_dict, user_id=user_id)
    session.add(db_conversation)
    await session.flush()
    await session.refresh(db_conversation)
    return db_conversation

async def delete_conversation(conversation_id: int, user_id: int, session: AsyncSession) -> bool:
    conversation = await get_conversation_by_id(
          conversation_id=conversation_id,
          user_id=user_id,
          session=session,
      )
    if not conversation:
        return False

    conversation.deleted_at = datetime.now(timezone.utc)
    session.add(conversation)
    await session.flush()
    return True

async def get_conversations_by_user(user_id: int, session: AsyncSession) -> List[Conversation]:
    statement = select(Conversation).where(Conversation.user_id == user_id, Conversation.deleted_at.is_(None))
    result = await session.exec(statement)
    return result.all()

async def get_conversation_by_id(conversation_id: int, user_id: int, session: AsyncSession) -> Conversation | None:
    statement = select(Conversation).where(Conversation.conversation_id == conversation_id, 
                                           Conversation.user_id == user_id,
                                           Conversation.deleted_at.is_(None))
    result = await session.exec(statement)
    return result.one_or_none()