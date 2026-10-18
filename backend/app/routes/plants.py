"""
Plant collection routes: CRUD, watering history, reminders.

Every operation is scoped to the authenticated user (from the JWT). A client
can never specify another user's id — ownership is enforced in the data layer.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.core.errors import NotFoundError
from app.db.store import UserRecord, get_store
from app.schemas.collection import (
    PlantCreate,
    PlantRecord,
    PlantSummary,
    PlantUpdate,
    PostponeRequest,
    ReminderUpdate,
    WateringEvent,
    WateringEventCreate,
)

router = APIRouter(prefix="/api/v1/plants", tags=["Plants"])


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _summary(plant: PlantRecord) -> PlantSummary:
    return PlantSummary(
        id=plant.id,
        name=plant.name,
        species=plant.species,
        location=plant.location,
        watering_interval_days=plant.watering_interval_days,
        reminder_enabled=plant.reminder_enabled,
        last_watered_at=plant.last_watered_at,
        next_watering_at=plant.next_watering_at,
        photo_path=plant.photo_path,
        created_at=plant.created_at,
    )


@router.get("", response_model=List[PlantSummary], summary="List my plants")
async def list_plants(user: UserRecord = Depends(get_current_user)) -> List[PlantSummary]:
    plants = await get_store().list_plants(user.id)
    return [_summary(p) for p in plants]


@router.post("", response_model=PlantRecord, status_code=201, summary="Add a plant")
async def create_plant(body: PlantCreate, user: UserRecord = Depends(get_current_user)) -> PlantRecord:
    plant = PlantRecord(id=uuid.uuid4().hex, user_id=user.id, **body.model_dump())
    plant.next_watering_at = plant.compute_next_watering()
    return await get_store().create_plant(plant)


@router.get("/{plant_id}", response_model=PlantRecord, summary="Plant details")
async def get_plant(plant_id: str, user: UserRecord = Depends(get_current_user)) -> PlantRecord:
    plant = await get_store().get_plant(user.id, plant_id)
    if plant is None:
        raise NotFoundError("Plant not found.")
    return plant


@router.patch("/{plant_id}", response_model=PlantRecord, summary="Edit a plant")
async def update_plant(
    plant_id: str, body: PlantUpdate, user: UserRecord = Depends(get_current_user)
) -> PlantRecord:
    store = get_store()
    plant = await store.get_plant(user.id, plant_id)
    if plant is None:
        raise NotFoundError("Plant not found.")
    updates = body.model_dump(exclude_unset=True)
    merged = plant.model_copy(update=updates)
    if "watering_interval_days" in updates:
        merged.next_watering_at = merged.compute_next_watering()
    return await store.update_plant(user.id, plant_id, merged)


@router.delete("/{plant_id}", status_code=204, summary="Delete a plant")
async def delete_plant(plant_id: str, user: UserRecord = Depends(get_current_user)) -> None:
    deleted = await get_store().delete_plant(user.id, plant_id)
    if not deleted:
        raise NotFoundError("Plant not found.")


@router.post("/{plant_id}/waterings", response_model=PlantRecord, summary="Record a watering")
async def record_watering(
    plant_id: str, body: WateringEventCreate, user: UserRecord = Depends(get_current_user)
) -> PlantRecord:
    store = get_store()
    watered_at = body.watered_at or _now()
    if watered_at.tzinfo is None:
        watered_at = watered_at.replace(tzinfo=timezone.utc)
    if watered_at > _now() + timedelta(minutes=5):
        from app.core.errors import AppError

        raise AppError(
            "Watering time cannot be in the future.", status_code=422, code="validation_error"
        )
    event = WateringEvent(
        id=uuid.uuid4().hex,
        plant_id=plant_id,
        user_id=user.id,
        watered_at=watered_at,
        notes=body.notes,
    )
    plant = await store.add_watering(user.id, plant_id, event)
    if plant is None:
        raise NotFoundError("Plant not found.")
    return plant


@router.get("/{plant_id}/waterings", response_model=List[WateringEvent], summary="Watering history")
async def watering_history(plant_id: str, user: UserRecord = Depends(get_current_user)) -> List[WateringEvent]:
    plant = await get_store().get_plant(user.id, plant_id)
    if plant is None:
        raise NotFoundError("Plant not found.")
    return sorted(plant.watering_history, key=lambda e: e.watered_at, reverse=True)


@router.patch("/{plant_id}/reminder", response_model=PlantRecord, summary="Update reminder settings")
async def update_reminder(
    plant_id: str, body: ReminderUpdate, user: UserRecord = Depends(get_current_user)
) -> PlantRecord:
    store = get_store()
    plant = await store.get_plant(user.id, plant_id)
    if plant is None:
        raise NotFoundError("Plant not found.")
    plant.reminder_enabled = body.reminder_enabled
    if body.watering_interval_days is not None:
        plant.watering_interval_days = body.watering_interval_days
        plant.next_watering_at = plant.compute_next_watering()
    return await store.update_plant(user.id, plant_id, plant)


@router.post("/{plant_id}/postpone", response_model=PlantRecord, summary="Postpone next watering")
async def postpone_watering(
    plant_id: str, body: PostponeRequest, user: UserRecord = Depends(get_current_user)
) -> PlantRecord:
    store = get_store()
    plant = await store.get_plant(user.id, plant_id)
    if plant is None:
        raise NotFoundError("Plant not found.")
    base = plant.next_watering_at or _now()
    if base.tzinfo is None:
        base = base.replace(tzinfo=timezone.utc)
    plant.reminder_postponed_until = base + timedelta(days=body.days)
    plant.next_watering_at = plant.reminder_postponed_until
    return await store.update_plant(user.id, plant_id, plant)
