"""
Collection-related Pydantic schemas: user-owned plants and watering history.

Timestamps are stored as timezone-aware UTC ISO-8601 strings.
"""

from datetime import datetime, timezone
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class WateringEvent(BaseModel):
    """A single recorded watering event."""

    id: str
    plant_id: str
    user_id: str
    watered_at: datetime
    notes: Optional[str] = Field(default=None, max_length=500)


class WateringEventCreate(BaseModel):
    watered_at: Optional[datetime] = None
    notes: Optional[str] = Field(default=None, max_length=500)


class PlantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    species: Optional[str] = Field(default=None, max_length=120)
    location: Optional[str] = Field(default=None, max_length=120)
    sunlight: Optional[str] = Field(default=None, max_length=60)
    soil_type: Optional[str] = Field(default=None, max_length=60)
    climate: Optional[str] = Field(default=None, max_length=60)
    care_notes: Optional[str] = Field(default=None, max_length=2000)
    # AI recommendation only — a suggestion, not a guarantee.
    watering_interval_days: int = Field(default=7, ge=1, le=365)
    reminder_enabled: bool = True
    photo_path: Optional[str] = Field(default=None, max_length=300)

    @field_validator("name", "species", "location", "sunlight", "soil_type", "climate")
    @classmethod
    def _strip(cls, v):
        return v.strip() if isinstance(v, str) else v


class PlantCreate(PlantBase):
    pass


class PlantUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    species: Optional[str] = Field(default=None, max_length=120)
    location: Optional[str] = Field(default=None, max_length=120)
    sunlight: Optional[str] = Field(default=None, max_length=60)
    soil_type: Optional[str] = Field(default=None, max_length=60)
    climate: Optional[str] = Field(default=None, max_length=60)
    care_notes: Optional[str] = Field(default=None, max_length=2000)
    watering_interval_days: Optional[int] = Field(default=None, ge=1, le=365)
    reminder_enabled: Optional[bool] = None

    @field_validator("name", "species", "location", "sunlight", "soil_type", "climate")
    @classmethod
    def _strip(cls, v):
        return v.strip() if isinstance(v, str) else v


class PlantRecord(PlantBase):
    """Full plant record as persisted."""

    id: str
    user_id: str
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    last_watered_at: Optional[datetime] = None
    next_watering_at: Optional[datetime] = None
    reminder_postponed_until: Optional[datetime] = None
    watering_history: List[WateringEvent] = Field(default_factory=list)

    def compute_next_watering(self) -> Optional[datetime]:
        """
        Compute next watering from last_watered_at + interval.

        If never watered, schedule from creation date so reminders still work.
        """
        base = self.last_watered_at or self.created_at
        from datetime import timedelta

        return base + timedelta(days=self.watering_interval_days)


class PlantSummary(BaseModel):
    """List-view shape (no full history)."""

    id: str
    name: str
    species: Optional[str] = None
    location: Optional[str] = None
    watering_interval_days: int
    reminder_enabled: bool
    last_watered_at: Optional[datetime] = None
    next_watering_at: Optional[datetime] = None
    photo_path: Optional[str] = None
    created_at: datetime


class ReminderUpdate(BaseModel):
    reminder_enabled: bool
    watering_interval_days: Optional[int] = Field(default=None, ge=1, le=365)


class PostponeRequest(BaseModel):
    """Postpone the next watering by a number of days (1-30)."""

    days: int = Field(..., ge=1, le=30)
