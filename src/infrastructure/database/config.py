from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import os
from src.infrastructure.database.base import Base

# URL de conexión asíncrona para PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://newsbrief_user:secret_password@localhost:5432/newsbrief_db")

engine = create_async_engine(DATABASE_URL, echo=False) # echo=True para debugear SQL

# SessionLocal es una fábrica de sesiones
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Función helper para obtener dependencias en FastAPI más adelante
async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session