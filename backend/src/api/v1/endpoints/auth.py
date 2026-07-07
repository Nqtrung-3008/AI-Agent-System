from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.src.dependencies import get_session
from backend.src.services import user_services
from backend.src.schemas.schemas import UserRegister, UserLogin, UserPublic, Token
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post('/register',
             status_code=status.HTTP_201_CREATED,
             response_model=UserPublic
             )
async def register(
    user_data: UserRegister,
    session: AsyncSession = Depends(get_session)
):
    new_user = await user_services.register_user(user_data=user_data, session=session)
    return new_user

@router.post('/login', response_model=Token)
async def login(
    data: UserLogin,
    session: AsyncSession = Depends(get_session)
):
    user_data = UserLogin(
        username=data.username,
        password=data.password
    )

    return await user_services.login_user(user=user_data, session=session)
