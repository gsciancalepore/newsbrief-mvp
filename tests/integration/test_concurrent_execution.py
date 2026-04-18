import pytest
import uuid
import os
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from src.infrastructure.celery.tasks import generate_daily_briefing_task
from src.infrastructure.database.models import BriefingModel, UserPreferenceModel
from src.domain.models.preference import UserPreference
from src.domain.value_objects.topic import Topic
from src.domain.value_objects.tone import Tone
from src.infrastructure.database.repositories import SqlAlchemyPreferenceRepository


DOCKER_DB_URL = os.getenv(
    "INTEGRATION_DATABASE_URL",
    "postgresql+asyncpg://newsbrief_user:secret_password@db:5432/newsbrief_db"
)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_concurrent_tasks_complete_without_db_errors():
    """
    Valida que N tasks concurrentes completen sin errores de DB.
    
    Requiere: docker-compose up (worker y db corriendo)
    """
    docker_engine = create_async_engine(DOCKER_DB_URL, poolclass=NullPool, pool_pre_ping=True)
    async_session = async_sessionmaker(docker_engine, class_=AsyncSession, expire_on_commit=False)
    
    # === SETUP: Crear 10 usuarios con preferencias ===
    user_ids = [str(uuid.uuid4()) for _ in range(10)]
    
    async with async_session() as session:
        pref_repo = SqlAlchemyPreferenceRepository(session)
        for uid in user_ids:
            pref = UserPreference(
                user_id=uuid.UUID(uid),
                topic=Topic("general"),
                tone=Tone.FORMAL,
                is_active=True
            )
            await pref_repo.save(pref)
        await session.commit()
    
    try:
        # === EJECUCIÓN: Encolar y esperar ===
        tasks = [generate_daily_briefing_task.delay(uid) for uid in user_ids]
        
        # Assert 1: Ninguna tarea lanza excepción
        for task in tasks:
            task.get(timeout=300)
        
        # === VERIFICACIÓN: Assert 2 ===
        async with async_session() as session:
            uuids = [uuid.UUID(uid) for uid in user_ids]
            stmt = select(BriefingModel).where(BriefingModel.user_id.in_(uuids))
            result = await session.execute(stmt)
            briefings = result.scalars().all()
        
        assert len(briefings) == 10, f"Se esperaban 10 briefings, encontrados {len(briefings)}"
    
    finally:
        # === TEARDOWN: Cleanup con sesión nueva e independiente ===
        async with async_session() as cleanup_session:
            # Eliminar briefings
            uuids = [uuid.UUID(uid) for uid in user_ids]
            await cleanup_session.execute(
                delete(BriefingModel).where(BriefingModel.user_id.in_(uuids))
            )
            # Eliminar preferencias
            await cleanup_session.execute(
                delete(UserPreferenceModel).where(UserPreferenceModel.user_id.in_(uuids))
            )
            await cleanup_session.commit()
        
        await docker_engine.dispose()