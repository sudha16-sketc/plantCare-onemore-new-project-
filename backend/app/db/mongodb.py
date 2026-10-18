"""
MongoDB store (Motor async driver).

Used when MONGODB_URI is configured. All plant reads/updates are scoped by
user_id so per-user isolation is enforced at the data layer, not the client.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.db.store import BaseStore, UserRecord
from app.schemas.collection import PlantRecord, WateringEvent


def _now() -> datetime:
    return datetime.now(timezone.utc)


class MongoStore(BaseStore):
    mode = "mongodb"

    def __init__(self, uri: str, db_name: str, timeout_ms: int = 5000) -> None:
        from motor.motor_asyncio import AsyncIOMotorClient

        self._client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=timeout_ms)
        self._db = self._client[db_name]
        self._users = self._db["users"]
        self._plants = self._db["plants"]

    # --- users ---
    async def create_user(self, email: str, username: str, password_hash: str) -> UserRecord:
        key = email.lower()
        existing = await self._users.find_one({"email": key})
        if existing:
            raise ValueError("An account with this email already exists")
        doc = {
            "id": uuid.uuid4().hex,
            "email": key,
            "username": username,
            "password_hash": password_hash,
            "created_at": _now(),
        }
        await self._users.insert_one(doc)
        return UserRecord(doc["id"], doc["email"], doc["username"], doc["password_hash"], doc["created_at"])

    async def get_user_by_email(self, email: str) -> Optional[UserRecord]:
        doc = await self._users.find_one({"email": email.lower()})
        if not doc:
            return None
        return UserRecord(doc["id"], doc["email"], doc["username"], doc["password_hash"], doc.get("created_at"))

    async def get_user_by_id(self, user_id: str) -> Optional[UserRecord]:
        doc = await self._users.find_one({"id": user_id})
        if not doc:
            return None
        return UserRecord(doc["id"], doc["email"], doc["username"], doc["password_hash"], doc.get("created_at"))

    async def update_user(self, user_id: str, username: Optional[str], email: Optional[str]) -> Optional[UserRecord]:
        updates: Dict = {}
        if username:
            updates["username"] = username
        if email:
            key = email.lower()
            existing = await self._users.find_one({"email": key})
            if existing and existing["id"] != user_id:
                raise ValueError("An account with this email already exists")
            updates["email"] = key
        if updates:
            await self._users.update_one({"id": user_id}, {"$set": updates})
        return await self.get_user_by_id(user_id)

    # --- plants ---
    async def create_plant(self, plant: PlantRecord) -> PlantRecord:
        doc = plant.model_dump(mode="json")
        await self._plants.insert_one(dict(doc))
        return plant

    async def list_plants(self, user_id: str) -> List[PlantRecord]:
        cursor = self._plants.find({"user_id": user_id})
        return [PlantRecord(**doc) async for doc in cursor]

    async def get_plant(self, user_id: str, plant_id: str) -> Optional[PlantRecord]:
        doc = await self._plants.find_one({"id": plant_id, "user_id": user_id})
        return PlantRecord(**doc) if doc else None

    async def update_plant(self, user_id: str, plant_id: str, plant: PlantRecord) -> Optional[PlantRecord]:
        plant.updated_at = _now()
        result = await self._plants.replace_one(
            {"id": plant_id, "user_id": user_id}, plant.model_dump(mode="json")
        )
        return plant if result.matched_count else None

    async def delete_plant(self, user_id: str, plant_id: str) -> bool:
        result = await self._plants.delete_one({"id": plant_id, "user_id": user_id})
        return result.deleted_count > 0

    async def add_watering(self, user_id: str, plant_id: str, event: WateringEvent) -> Optional[PlantRecord]:
        plant = await self.get_plant(user_id, plant_id)
        if not plant:
            return None
        plant.watering_history.append(event)
        plant.last_watered_at = event.watered_at
        plant.next_watering_at = plant.compute_next_watering()
        plant.updated_at = _now()
        await self._plants.replace_one(
            {"id": plant_id, "user_id": user_id}, plant.model_dump(mode="json")
        )
        return plant

    async def ping(self) -> bool:
        try:
            await self._client.admin.command("ping")
            return True
        except Exception:
            return False

    async def close(self) -> None:
        self._client.close()

    async def ensure_indexes(self) -> None:
        """Create useful indexes (call from init script or startup)."""
        await self._users.create_index("email", unique=True)
        await self._plants.create_index("user_id")
        await self._plants.create_index([("user_id", 1), ("id", 1)])
