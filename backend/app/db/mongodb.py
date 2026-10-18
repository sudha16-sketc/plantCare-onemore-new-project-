from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB", "plantcare")

# Lazy initialization - connection happens on first use
_client = None
_db = None

def _get_client():
    """Get or create MongoDB client (lazy initialization)."""
    global _client
    if _client is None:
        try:
            if not MONGODB_URI:
                raise ValueError("MONGODB_URI not configured in .env")
            _client = AsyncIOMotorClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        except Exception as e:
            print(f"⚠ MongoDB initialization warning: {e}")
            return None
    return _client

def _get_db():
    """Get database instance."""
    global _db
    if _db is None:
        client = _get_client()
        if client is not None:
            _db = client[DB_NAME]
    return _db

# Collections - created on demand
plant_guides_collection = None
users_collection = None
plants_collection = None
notifications_collection = None

def _init_collections():
    """Initialize collection references."""
    global plant_guides_collection, users_collection, plants_collection, notifications_collection
    db = _get_db()
    if db is not None:
        plant_guides_collection = db["plant_guides"]
        users_collection = db["users"]
        plants_collection = db["plants"]
        notifications_collection = db["notifications"]
        return True
    return False

# Initialize on first import
_init_collections()

# Provide access functions for dynamic initialization
async def get_collections():
    """Get all collections, initializing if needed."""
    global plant_guides_collection, users_collection, plants_collection, notifications_collection
    _init_collections()
    return {
        "plant_guides": plant_guides_collection,
        "users": users_collection,
        "plants": plants_collection,
        "notifications": notifications_collection
    }
