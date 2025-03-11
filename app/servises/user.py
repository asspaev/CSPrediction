from sqlalchemy.ext.asyncio import AsyncSession
from models import User
from schemas import user as schemas_user
from sqlalchemy import select
from datetime import datetime
from utils import hash_string
from fastapi import HTTPException


async def create_user(
        session: AsyncSession,
        user_register: schemas_user.UserRegister,
) -> User:
    user = await session.execute(
        select(User).filter_by(email=user_register.email)
    )
    if user.scalar():
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    else:
        user = User(
            email=user_register.email,
            password_hash=hash_string(user_register.password),
            created_at=datetime.now(),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
    
async def auth_user(
        session: AsyncSession,
        user_login: schemas_user.UserRegister,
) -> User:
    user = await session.execute(
        select(User).filter_by(email=user_login.email)
    )
    user = user.scalar()
    if user:
        if user.password_hash == hash_string(user_login.password):
            return user
        else:
            raise HTTPException(status_code=400, detail="Неверный пароль!")
    else:
        raise HTTPException(status_code=400, detail="Пользователя с таким email не существует")