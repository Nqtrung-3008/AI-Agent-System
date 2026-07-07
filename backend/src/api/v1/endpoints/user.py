from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.src.dependencies import get_session, get_current_user
from backend.src.services import user_services
from backend.src.schemas.schemas import UserPublic

router = APIRouter()

@router.get('/me', response_model=UserPublic)
async def get_me(current_user=Depends(get_current_user)):
    return current_user

@router.get('/{user_id}', response_model=UserPublic)
async def get_user(user_id:int, session=Depends(get_session), current_user=Depends(get_current_user)):
    user = await user_services.get_user_by_id(user_id=user_id, session=session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user