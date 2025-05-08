from sqlalchemy.ext.asyncio import AsyncSession
from schemas import user as schemas_user
from sqlalchemy import select
from datetime import datetime
from utils import hash_string
from fastapi import HTTPException

from sql_models import Model


async def get_all_models(
    session: AsyncSession,
) -> list[Model]:
    stmt = select(Model)
    result = await session.execute(stmt)
    models = result.scalars().all()
    return models


async def get_model_by_id(
    model_id: int, 
    session: AsyncSession,
) -> Model | None:
    stmt = select(Model).where(Model.id == model_id)
    result = await session.execute(stmt)
    model = result.scalar_one_or_none()
    return model