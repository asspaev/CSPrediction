from sqlalchemy.ext.asyncio import AsyncSession
from sql_models.prediction import Prediction
from sql_models.user import User
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException


async def create_prediction(
    session: AsyncSession,
    user_id: int,
    model_id: int,
    input_text: str,
    team_winner: str,
    team_loser: str,
    credits_used: float
) -> int:
    new_prediction = Prediction(
        user_id=user_id,
        model_id=model_id,
        input_text=input_text,
        team_winner=team_winner,
        team_loser=team_loser,
        credits_used=credits_used,
        created_at=datetime.now(),
    )

    session.add(new_prediction)
    await session.flush()  # Получение ID до коммита
    await session.commit()

    return new_prediction.id

async def get_predictions_by_login(
    session: AsyncSession, 
    login: str,
) -> list[Prediction]:
    result = await session.execute(
        select(User)
        .options(selectinload(User.predictions).selectinload(Prediction.model))  # подгрузка модели
        .where(User.login == login)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user.predictions