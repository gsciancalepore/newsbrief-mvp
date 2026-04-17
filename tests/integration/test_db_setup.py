import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from src.infrastructure.database.config import Base, DATABASE_URL
from src.infrastructure.database.models import UserPreferenceModel # Importar para registrar metadata

@pytest.mark.asyncio
async def test_create_tables():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()