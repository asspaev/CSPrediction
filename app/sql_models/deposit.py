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


class Deposit(IntIdPkMixin, Base):
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP)
    
    user = relationship("User", back_populates="deposits")