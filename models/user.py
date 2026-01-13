"""User model."""
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database.db import Base
import uuid


class User(Base):
    """User account."""

    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    api_key = Column(String, unique=True, nullable=False, default=lambda: str(uuid.uuid4()))

    # OAuth tokens
    truecoach_token = Column(String, nullable=True)
    truecoach_refresh_token = Column(String, nullable=True)
    truecoach_connected = Column(Boolean, default=False)

    mfp_token = Column(String, nullable=True)
    mfp_connected = Column(Boolean, default=False)

    # Settings
    sync_enabled = Column(Boolean, default=True)
    last_sync = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workouts = relationship("Workout", back_populates="user", cascade="all, delete-orphan")
    nutrition = relationship("Nutrition", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"
