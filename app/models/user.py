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


class User(IntIdPkMixin, Base):
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP)
    credits: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    
    predictions = relationship("Prediction", back_populates="user")
    deposits = relationship("Deposit", back_populates="user")
    spends = relationship("Spend", back_populates="user")