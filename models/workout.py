"""Workout model."""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from database.db import Base
import uuid


class Workout(Base):
    """Workout session data."""

    __tablename__ = "workouts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # Workout details
    date = Column(Date, nullable=False, index=True)
    title = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    coach_notes = Column(String, nullable=True)

    # Metrics
    duration_minutes = Column(Integer, nullable=True)
    exercises = Column(JSON, nullable=True)  # List of exercises with sets/reps/weight
    total_volume = Column(Float, nullable=True)  # Total weight x reps

    # Source
    source = Column(String, default="truecoach")  # truecoach, manual, etc.
    external_id = Column(String, nullable=True)  # ID from TrueCoach

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="workouts")

    def __repr__(self):
        return f"<Workout {self.date} - {self.title}>"
