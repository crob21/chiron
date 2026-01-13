"""Nutrition model."""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from database.db import Base
import uuid


class Nutrition(Base):
    """Daily nutrition data."""

    __tablename__ = "nutrition"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # Date
    date = Column(Date, nullable=False, index=True)

    # Macros
    calories = Column(Integer, nullable=True)
    protein = Column(Float, nullable=True)
    carbs = Column(Float, nullable=True)
    fat = Column(Float, nullable=True)
    fiber = Column(Float, nullable=True)

    # Additional metrics
    water_ml = Column(Integer, nullable=True)
    weight_kg = Column(Float, nullable=True)

    # Source
    source = Column(String, default="myfitnesspal")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="nutrition")

    def __repr__(self):
        return f"<Nutrition {self.date} - {self.calories}cal>"
