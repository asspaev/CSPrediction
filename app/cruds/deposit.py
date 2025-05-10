from sqlalchemy.ext.asyncio import AsyncSession
from sql_models.deposit import Deposit
from datetime import datetime




async def add_deposit(
    session: AsyncSession, 
    user_id: int, 
    amount: float,
):
    # Создание нового объекта депозита
    deposit = Deposit(
        user_id=user_id,
        amount=amount,
        created_at=datetime.now(),
    )
    
    # Добавление депозита в сессию
    session.add(deposit)
    
    # Коммит транзакции
    await session.commit()

    # Возвращаем добавленный депозит (если нужно)
    return deposit