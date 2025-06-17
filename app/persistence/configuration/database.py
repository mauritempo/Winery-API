from typing import AsyncGenerator
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession,create_async_engine,async_sessionmaker
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Connecting to database at {DATABASE_URL}")


engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


