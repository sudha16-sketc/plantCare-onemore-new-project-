"""
In-memory store for development, demos, and automated tests.

Data is process-local and lost on restart. /ready reports storage_mode:
"memory" so clients know this is not persistent storage.
"""

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.db.store import BaseStore, UserRecord
from app.schemas.collection import PlantRecord, WateringEvent


def _now() -> datetime:
    return datetime.now(timezone.utc)


class MemoryStore(BaseStore):
    mode = "memory"

    def __init__(self) -> None:
        self._users: Dict[str, UserRecord] = {}
        self._users_by_email: Dict[str, str] = {}
        self._plants: Dict[str, PlantRecord] = {}
        self._lock = asyncio.Lock()

    # --- users ---
    async def create_user(self, email: str, username: str, password_hash: str) -> UserRecord:
        async with self._lock:
            key = email.lower()
            if key in self._users_by_email:
                raise ValueError("An account with this email already exists")
            user = UserRecord(uuid.uuid4().hex, key, username, password_hash, _now())
            self._users[user.id] = user
            self._users_by_email[key] = user.id
            return user

    async def get_user_by_email(self, email: str) -> Optional[UserRecord]:
        uid = self._users_by_email.get(email.lower())
        return self._users.get(uid) if uid else None

    async def get_user_by_id(self, user_id: str) -> Optional[UserRecord]:
        return self._users.get(user_id)

    async def update_user(self, user_id: str, username: Optional[str], email: Optional[str]) -> Optional[UserRecord]:
        async with self._lock:
            user = self._users.get(user_id)
            if not user:
                return None
            if email and email.lower() != user.email:
                if email.lower() in self._users_by_email:
                    raise ValueError("An account with this email already exists")
                del self._users_by_email[user.email]
                user.email = email.lower()
                self._users_by_email[user.email] = user_id
            if username:
                user.username = username
            return user

    # --- plants ---
    async def create_plant(self, plant: PlantRecord) -> PlantRecord:
        async with self._lock:
            self._plants[plant.id] = plant.model_copy(deep=True)
            return self._plants[plant.id].model_copy(deep=True)

    async def list_plants(self, user_id: str) -> List[PlantRecord]:
        return [
            p.model_copy(deep=True)
            for p in self._plants.values()
            if p.user_id == user_id
        ]

    async def get_plant(self, user_id: str, plant_id: str) -> Optional[PlantRecord]:
        plant = self._plants.get(plant_id)
        if plant and plant.user_id == user_id:
            return plant.model_copy(deep=True)
        return None

    async def update_plant(self, user_id: str, plant_id: str, plant: PlantRecord) -> Optional[PlantRecord]:
        async with self._lock:
            existing = self._plants.get(plant_id)
            if not existing or existing.user_id != user_id:
                return None
            plant.updated_at = _now()
            self._plants[plant_id] = plant.model_copy(deep=True)
            return plant.model_copy(deep=True)

    async def delete_plant(self, user_id: str, plant_id: str) -> bool:
        async with self._lock:
            plant = self._plants.get(plant_id)
            if not plant or plant.user_id != user_id:
                return False
            del self._plants[plant_id]
            return True

    async def add_watering(self, user_id: str, plant_id: str, event: WateringEvent) -> Optional[PlantRecord]:
        async with self._lock:
            plant = self._plants.get(plant_id)
            if not plant or plant.user_id != user_id:
                return None
            plant.watering_history.append(event)
            plant.last_watered_at = event.watered_at
            plant.next_watering_at = plant.compute_next_watering()
            plant.updated_at = _now()
            return plant.model_copy(deep=True)

    async def ping(self) -> bool:
        return True
