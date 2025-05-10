from sqlalchemy.ext.asyncio import AsyncSession
from sql_models.deposit import Deposit
from sql_models.spend import Spend
from datetime import datetime
from sqlalchemy import select, union_all, literal
from sqlalchemy.orm import aliased
from fastapi import HTTPException

async def get_user_transactions(session: AsyncSession, user_id: int):
    deposits_alias = aliased(Deposit)
    spends_alias   = aliased(Spend)

    # 1) Депозиты: transaction_spend = 0.0
    deposits_q = select(
        deposits_alias.id.label("transaction_id"),
        deposits_alias.created_at.label("transaction_date"),
        literal(0.0).label("transaction_predict_id"),   # вместо NULL можно оставить 0.0, или func.null()
        deposits_alias.amount.label("transaction_deposit"),
        literal(0.0).label("transaction_spend"),        # теперь числовой ноль
    ).where(deposits_alias.user_id == user_id)

    # 2) Списания: transaction_deposit = 0.0
    spends_q = select(
        spends_alias.id.label("transaction_id"),
        spends_alias.created_at.label("transaction_date"),
        spends_alias.prediction_id.label("transaction_predict_id"),
        literal(0.0).label("transaction_deposit"),     # числовой ноль
        spends_alias.amount.label("transaction_spend"), # сумма расхода
    ).where(spends_alias.user_id == user_id)

    # 3) Объединяем и оборачиваем в подзапрос
    union_subq = union_all(deposits_q, spends_q).subquery()

    # 4) Финальный select с сортировкой по дате
    final_q = select(
        union_subq.c.transaction_id,
        union_subq.c.transaction_date,
        union_subq.c.transaction_predict_id,
        union_subq.c.transaction_deposit,
        union_subq.c.transaction_spend,
    ).order_by(union_subq.c.transaction_date.desc())

    # 5) Выполняем и собираем в список словарей
    result = await session.execute(final_q)
    rows = result.all()

    # Формируем результат как список словарей
    return [
        {
            "id": f"D-{row.transaction_id}" if row.transaction_deposit else f"S-{row.transaction_id}",
            "date": row.transaction_date,
            "predict_id": int(row.transaction_predict_id) if row.transaction_predict_id else "—",
            "deposit": "Пополнение" if row.transaction_deposit else False,
            "spend": "Списание" if row.transaction_spend else False,
            "amount_int": int(row.transaction_deposit) if row.transaction_deposit else int(row.transaction_spend),
            "amount_float": '.' + str(f"{row.transaction_deposit:.2f}".split('.')[1]) if row.transaction_deposit else '.' + str(f"{row.transaction_spend:.2f}".split('.')[1]),
        }
        for row in rows
    ]