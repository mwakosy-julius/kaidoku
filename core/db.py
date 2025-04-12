from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
from contextlib import asynccontextmanager

client = None
db = None
user_collection = None

try:
    client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
    print(f"MongoDB connection successful {settings.MONGODB_URL}")
    client.admin.command("ping")
    db = client.get_database("kaidoku")
    user_collection = db.get_collection("users")
    print("MongoDB connection successful")
except Exception as e:
    print(f"MongoDB connection error: {e}")


@asynccontextmanager
async def get_session():
    """Get MongoDB session with proper async context management"""
    if client is None:
        raise ConnectionError("MongoDB client is not initialized")

    session = await client.start_session()
    try:
        yield session
    finally:
        await session.end_session()


async def init_db():
    """Initialize database connection asynchronously"""
    global client, db, user_collection

    try:
        if client is None:
            client = AsyncIOMotorClient(settings.MONGODB_URL)
            db = client.get_database("kaidoku")
            user_collection = db.get_collection("users")

        await client.admin.command("ping")
        print("MongoDB connection verified asynchronously")
        return True
    except Exception as e:
        print(f"MongoDB async initialization error: {e}")
        return False
