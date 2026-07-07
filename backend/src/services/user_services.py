from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.src.models.models import Users
from backend.src.schemas.schemas import UserRegister, UserLogin
from backend.src.core.security import hash_password, verify_password, create_access_token
from fastapi import HTTPException, status

async def register_user(user_data: UserRegister, session: AsyncSession) -> Users:
    existing_user = await session.exec(
    select(Users).where(Users.username == user_data.username)
)
    if existing_user.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )
    
    hashed_password = hash_password(user_data.password)
    user_dict = user_data.model_dump(exclude={'password'})
    db_user = Users(**user_dict, password=hashed_password)
    session.add(db_user)
    await session.flush()
    await session.refresh(db_user)
    return db_user

async def login_user(user: UserLogin, session: AsyncSession):
    result = await session.exec(
        select(Users).where(Users.username == user.username)
    )
    db_user = result.first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    if not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    token = create_access_token({"user_id": db_user.user_id})
    return {"access_token": token, 'token_type': 'bearer'}

async def get_user_by_id(user_id: int, session: AsyncSession) -> Users | None:
    statement = select(Users).where(Users.user_id == user_id)
    result = await session.exec(statement)
    return result.one_or_none()