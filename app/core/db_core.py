from sqlalchemy import text

from app.db.database import async_engine,  Base


async def create_tables():
    async with async_engine.begin() as conn:
        # await conn.execute(text("DROP TABLE IF EXISTS transactions CASCADE"))
        # await conn.execute(text("DROP TABLE IF EXISTS cards CASCADE"))
        # await conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        await conn.run_sync(Base.metadata.create_all)
    print("Tables are created!")




