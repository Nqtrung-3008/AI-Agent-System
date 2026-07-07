from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.src.dependencies import get_session, get_current_user
from backend.src.services import conversation_services, message_services
from backend.src.agent.agent_service import chat_with_agent
from backend.src.schemas.schemas import ChatRequest, ChatResponse, MessagePublic

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user)
):
    conversation = await conversation_services.get_conversation_by_id(conversation_id=req.conversation_id, 
                                                                       user_id=user.user_id, 
                                                                       session=session)

    if not conversation:
        raise HTTPException(404, "Session not found")
    
    result = await chat_with_agent(
        content=req.content,
        conversation_id=req.conversation_id,
        user_id=user.user_id,
        session=session
    )

    return {"answer": result}

@router.get("/messages/{conversation_id}", response_model = List[MessagePublic])
async def get_messages(conversation_id: int, 
                       session: AsyncSession = Depends(get_session),
                       user=Depends(get_current_user)
                       ):
    return await message_services.get_messages_by_conversation(conversation_id=conversation_id, user_id=user.user_id, session=session)