"""
Storage facade.

Two implementations share one interface:
- MongoStore  — MongoDB Atlas via Motor (production / persistent dev)
- MemoryStore — process-local dict store for dev, demos, and automated tests

The active store is exposed via get_store(). /ready reports which mode is live
so nothing pretends to be a database that is not.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.schemas.collection import PlantRecord, WateringEvent
from app.utils.config import settings


class UserRecord:
    __slots__ = ("id", "email", "username", "password_hash", "created_at")

    def __init__(self, id: str, email: str, username: str, password_hash: str, created_at):
        self.id = id
        self.email = email
        self.username = username
        self.password_hash = password_hash
        self.created_at = created_at


class BaseStore(ABC):
    mode: str = "abstract"

    # --- users ---
    @abstractmethod
    async def create_user(self, email: str, username: str, password_hash: str) -> UserRecord: ...

    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[UserRecord]: ...

    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional[UserRecord]: ...

    @abstractmethod
    async def update_user(self, user_id: str, username: Optional[str], email: Optional[str]) -> Optional[UserRecord]: ...

    # --- plants ---
    @abstractmethod
    async def create_plant(self, plant: PlantRecord) -> PlantRecord: ...

    @abstractmethod
    async def list_plants(self, user_id: str) -> List[PlantRecord]: ...

    @abstractmethod
    async def get_plant(self, user_id: str, plant_id: str) -> Optional[PlantRecord]:
        """Ownership-scoped read: returns the plant only if it belongs to user_id."""

    @abstractmethod
    async def update_plant(self, user_id: str, plant_id: str, plant: PlantRecord) -> Optional[PlantRecord]: ...

    @abstractmethod
    async def delete_plant(self, user_id: str, plant_id: str) -> bool: ...

    @abstractmethod
    async def add_watering(self, user_id: str, plant_id: str, event: WateringEvent) -> Optional[PlantRecord]: ...

    @abstractmethod
    async def ping(self) -> bool:
        """Cheap health probe used by /ready."""

    async def close(self) -> None:  # pragma: no cover - trivial default
        return None


_store: Optional[BaseStore] = None


def get_store() -> BaseStore:
    """Return the process-wide store, creating it on first use."""
    global _store
    if _store is None:
        if settings.mongodb_uri:
            from app.db.mongodb import MongoStore

            _store = MongoStore(settings.mongodb_uri, settings.mongodb_db, settings.mongodb_timeout_ms)
        else:
            from app.db.memory import MemoryStore

            _store = MemoryStore()
    return _store


def set_store(store: BaseStore) -> None:
    """Override the store (used by tests)."""
    global _store
    _store = store


async def close_store() -> None:
    global _store
    if _store is not None:
        await _store.close()
        _store = None
