"""
Initialize database indexes (run once against a configured MongoDB):

    cd backend && python -m app.scripts.init_db

Requires MONGODB_URI in the environment. No-ops with a clear message when
the API is running in in-memory mode.
"""

import asyncio
import logging

from app.db.store import get_store
from app.utils.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("plantcare.init_db")


async def main() -> None:
    if not settings.mongodb_uri:
        logger.warning(
            "MONGODB_URI is not set — the API uses in-memory storage and has nothing to initialize."
        )
        return
    store = get_store()
    if hasattr(store, "ensure_indexes"):
        await store.ensure_indexes()
        logger.info("Database indexes ensured.")
    else:
        logger.warning("Active store does not support index creation.")
    await store.close()


if __name__ == "__main__":
    asyncio.run(main())
