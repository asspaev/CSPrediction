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


class Model(IntIdPkMixin, Base):
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP)
    price_per_prediction: Mapped[float] = mapped_column(Float)
    
    predictions = relationship("Prediction", back_populates="model")