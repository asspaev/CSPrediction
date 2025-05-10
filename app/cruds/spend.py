from sqlalchemy.ext.asyncio import AsyncSession
from sql_models.spend import Spend
from datetime import datetime


async def create_spend(
    session: AsyncSession,
    user_id: int,
    prediction_id: int,
    amount: float,
) -> None:
    new_spend = Spend(
        user_id=user_id,
        prediction_id=prediction_id,
        amount=amount,
        created_at=datetime.now(),
    )

    session.add(new_spend)
    await session.commit()