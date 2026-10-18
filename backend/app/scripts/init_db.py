import asyncio
from app.db.mongodb import (
    users_collection,
    plants_collection,
    plant_guides_collection,
    notifications_collection
)

async def init_indexes():
    """Initialize database indexes for collections."""
    indexes = [
        (users_collection, "email", {"unique": True}),
        (plants_collection, "user_id", {}),
        (plant_guides_collection, "plant_name", {}),
        (notifications_collection, "scheduled_at", {}),
    ]
    
    for collection, field, options in indexes:
        try:
            await collection.create_index(field, **options)
            print(f"✓ Created index on {collection.name}.{field}")
        except Exception as e:
            print(f"⚠ Index creation failed on {field}: {str(e)[:100]}")

async def main():
    """Main function to initialize database."""
    print("Initializing Plant Care database indexes...")
    await init_indexes()
    print("Database initialization complete.")

if __name__ == "__main__":
    asyncio.run(main())
