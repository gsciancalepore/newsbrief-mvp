import asyncio
import os
import logging
from uuid import UUID
from sqlalchemy import select, distinct

from src.infrastructure.celery.config import app
from src.infrastructure.database.config import AsyncSessionLocal
from src.infrastructure.database.repositories import SqlAlchemyPreferenceRepository, SqlAlchemyBriefingRepository
from src.infrastructure.external_api.gemini_adapter import GeminiSummarizerAdapter
from src.infrastructure.external_api.rss_adapter import RssNewsSource
from src.infrastructure.external_api.email_adapter import EmailNotificationAdapter
from src.infrastructure.database.models import UserPreferenceModel

from src.application.commands.generate_briefing import GenerateDailyBriefingCommand, GenerateDailyBriefingHandler
from src.application.services.news_fetcher_service import NewsFetcherService

logger = logging.getLogger(__name__)

@app.task(name="tasks.generate_daily_briefing_for_user")
def generate_daily_briefing_task(user_id_str: str):
    """
    Tarea asíncrona para generar el briefing de un usuario específico.
    """
    user_id = UUID(user_id_str)
    # Ejecutar el flujo asíncrono dentro de un event loop
    asyncio.run(_process_briefing(user_id))

async def _process_briefing(user_id: UUID):
    # 1. Crear una sesión de DB nueva para esta tarea
    async with AsyncSessionLocal() as session:
        try:
            # 2. Instanciar Repositorios (Infraestructura)
            pref_repo = SqlAlchemyPreferenceRepository(session=session)
            briefing_repo = SqlAlchemyBriefingRepository(session=session)
            
            # 3. Instanciar Servicios Externos (Adapters)
            news_source = RssNewsSource(feed_url="https://feeds.feedburner.com/TechCrunch/")
            news_service = NewsFetcherService(source=news_source)
            ai_service = GeminiSummarizerAdapter()
            
            # 4. Instanciar Servicio de Notificación
            notification_service = EmailNotificationAdapter()
            
            # 5. Instanciar el Handler (Aplicación)
            handler = GenerateDailyBriefingHandler(
                pref_repo=pref_repo,
                briefing_repo=briefing_repo,
                news_service=news_service,
                ai_service=ai_service,
                notification_service=notification_service
            )
            
            # 6. Ejecutar el Caso de Uso
            recipient_email = os.getenv("DEFAULT_RECIPIENT_EMAIL", "test@example.com")
            
            command = GenerateDailyBriefingCommand(
                user_id=user_id,
                recipient_email=recipient_email
            )
            await handler.execute(command)
            
            logger.info(f"Briefing generado y notificado para user {user_id}")
            
        except Exception as e:
            logger.error(f"Error generando briefing para user {user_id}: {e}")
            raise e

@app.task(name="tasks.trigger_all_users_briefings")
def trigger_all_users_briefings():
    """
    Obtiene todos los usuarios con preferencias activas y dispara una tarea para cada uno.
    """
    async def _trigger():
        async with AsyncSessionLocal() as session:
            # Query directa para obtener IDs únicos de usuarios con preferencias
            result = await session.execute(
                select(distinct(UserPreferenceModel.user_id))
            )
            user_ids = result.scalars().all()
            
            for uid in user_ids:
                # Disparar tarea individual para cada usuario
                generate_daily_briefing_task.delay(str(uid))
                logger.info(f"Tarea encolada para user: {uid}")

    asyncio.run(_trigger())