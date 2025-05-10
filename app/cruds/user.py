from sqlalchemy.ext.asyncio import AsyncSession
from sql_models.user import User
from schemas import user as schemas_user
from sqlalchemy import select, update
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
            login=user_register.login,
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
        select(User).filter_by(login=user_login.login)
    )
    user = user.scalar()
    if user:
        if user.password_hash == hash_string(user_login.password):
            return user
        else:
            raise HTTPException(status_code=400, detail="Неверный пароль!")
    else:
        raise HTTPException(status_code=400, detail="Пользователя с таким email не существует")


async def get_user_credits_by_email(
    session: AsyncSession,
    email: str, 
) -> float:
    stmt = select(User.credits).where(User.email == email)
    result = await session.execute(stmt)
    credits = result.scalar_one_or_none()
    return credits if credits is not None else 0.0


async def add_credits_by_email(
    session: AsyncSession,
    email: str, 
    amount: float, 
) -> None:
    # Проверка существования пользователя и текущего баланса
    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Обновление credits
    user.credits += amount
    await session.commit()

async def is_email_unique(
    session: AsyncSession, 
    email: str,
) -> bool:
    result = await session.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none() is None


async def is_login_unique(
    session: AsyncSession, 
    login: str,
) -> bool:
    result = await session.execute(
        select(User).where(User.login == login)
    )
    return result.scalar_one_or_none() is None


async def update_user_credits_by_login(
    session: AsyncSession,
    login: str,
    new_credits: float,
) -> None:
    await session.execute(
        update(User)
        .where(User.login == login)
        .values(credits=new_credits)
    )
    await session.commit()

async def get_user_id_by_login(
    session: AsyncSession, 
    login: str,
) -> int:
    result = await session.execute(
        select(User.id).where(User.login == login)
    )
    user_id = result.scalar()
    
    if user_id is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user_id