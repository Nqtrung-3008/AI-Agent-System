from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.src.dependencies import get_session, get_current_user
from backend.src.services import conversation_services
from backend.src.schemas.schemas import ConversationCreate, ConversationPublic, ConversationDelete

router = APIRouter()

@router.post('/', response_model=ConversationPublic)
async def create_session(conversation_data: ConversationCreate,
                         session: AsyncSession=Depends(get_session),
                         user=Depends(get_current_user)):
    
    return await conversation_services.create_conversation(conversation_data=conversation_data, user_id=user.user_id, session=session)

@router.get('/', response_model = List[ConversationPublic])
async def get_sessions(session: AsyncSession=Depends(get_session),
                       user=Depends(get_current_user)):
    return await conversation_services.get_conversations_by_user(user_id=user.user_id, session=session)

@router.delete('/{conversation_id}', response_model = ConversationDelete)
async def delete_sessions(conversation_id: int,
                          session: AsyncSession=Depends(get_session),
                          user=Depends(get_current_user)):
    deleted =  await conversation_services.delete_conversation(conversation_id=conversation_id, user_id=user.user_id, session=session)
    if not deleted:
      raise HTTPException(status_code=404, detail="Conversation not found")
    return {"deleted": True}