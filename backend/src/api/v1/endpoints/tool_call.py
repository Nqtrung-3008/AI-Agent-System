from fastapi import APIRouter, Depends
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.src.dependencies import get_session, get_current_user
from backend.src.services import tool_call_services
from backend.src.schemas.schemas import ToolCallPublic


router = APIRouter()

@router.get('/{conversation_id}', response_model = List[ToolCallPublic])
async def get_tool_calls(
    conversation_id: int,
    session: AsyncSession = Depends(get_session),
    user = Depends(get_current_user)
):
    return await tool_call_services.get_tool_calls_by_conversation(
        conversation_id=conversation_id,
        user_id=user.user_id,
        session=session
    )