from sqlalchemy.ext.asyncio import AsyncSession
from models import User
from schemas import user as schemas_user
from sqlalchemy import select
from datetime import datetime


async def create_user(
        session: AsyncSession,
        user_register: schemas_user.UserRegister,
) -> User:
    existing_user = await session.execute(
        select(User).filter_by(email=user_register.email)
    )
    if existing_user.scalar():
        raise ValueError("Пользователь с таким email уже существует")
    user = User(
        email=user_register.email,
        password_hash=user_register.password,  # TODO Заменить на хеш
        created_at=datetime.now(),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user