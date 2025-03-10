from sqlalchemy import (
    ForeignKey,
    String,
    Text,
    Float,
    Integer,
    TIMESTAMP,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from .mixins import IntIdPkMixin
from .base import Base


class Conversion(IntIdPkMixin, Base):
    deposit_id: Mapped[int] = mapped_column(Integer, ForeignKey("deposits.id"), nullable=False)
    rub_amount: Mapped[float] = mapped_column(Float, nullable=False)
    credits_amount: Mapped[float] = mapped_column(Float, nullable=False)
    exchange_rate: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP)
    
    deposit = relationship("Deposit", back_populates="conversions")