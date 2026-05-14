from app.config import DATABASE_URL

# Script to delete all data from the database. Use with caution!
from app.db import engine, AsyncSessionLocal
from app.models import Base

async def flush_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
if __name__ == "__main__":
    import asyncio
    asyncio.run(flush_db())