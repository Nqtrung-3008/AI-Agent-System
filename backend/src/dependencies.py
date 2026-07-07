from backend.src.core.session import AsyncSessionFactory
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.src.core.security import decode_token
from backend.src.models.models import Users

async def get_session():
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
):
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
)

    user_id = payload.get("user_id")

    result = await session.exec(
        select(Users).where(Users.user_id == user_id)
    )
    user = result.first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user