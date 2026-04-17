import pytest
import pytest_asyncio
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from src.infrastructure.database.models import Base

# URL de la BD de test (desde .env.test o hardcodeada)
TEST_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://newsbrief_user:secret_password@localhost:5432/newsbrief_test"
)

# Engine específico para tests (se crea lazily en el fixture)
_test_engine = None
_test_session_maker = None

@pytest.fixture(scope="session")
def event_loop():
    """Unifica el event loop para toda la suite."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    """
    Crea las tablas una sola vez al inicio de la suite de tests.
    Usa un engine específico para tests, creado en el contexto correcto.
    """
    global _test_engine
    
    # Crear engine para tests dentro del contexto de pytest (event loop correcto)
    _test_engine = create_async_engine(
        TEST_DATABASE_URL, 
        echo=False,
        poolclass=NullPool  # Evitar conflictos de conexiones entre event loops
    )
    
    # Limpiar tablas existentes y crear nuevas
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Cleanup al final (opcional, pero buena práctica)
    await _test_engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def db_session():
    """
    Nueva sesión por test con rollback.
    Usa el sessionmaker del engine de test.
    """
    global _test_session_maker
    
    if _test_session_maker is None:
        _test_session_maker = async_sessionmaker(
            _test_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async with _test_session_maker() as session:
        yield session
        await session.rollback()