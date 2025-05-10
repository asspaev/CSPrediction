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


class Prediction(IntIdPkMixin, Base):
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    model_id: Mapped[int] = mapped_column(Integer, ForeignKey("models.id"), nullable=False)
    input_text: Mapped[str] = mapped_column(Text, nullable=False)
    team_winner: Mapped[str] = mapped_column(String(48), nullable=False)
    team_loser: Mapped[str] = mapped_column(String(48), nullable=False)
    credits_used: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP)
    
    user = relationship("User", back_populates="predictions")
    model = relationship("Model", back_populates="predictions")
    spends = relationship("Spend", back_populates="prediction")