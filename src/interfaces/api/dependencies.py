from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# Infraestructura (DB & AI)
from src.infrastructure.database.config import get_session
from src.infrastructure.database.repositories import SqlAlchemyPreferenceRepository, SqlAlchemyBriefingRepository
from src.infrastructure.external_api.gemini_adapter import GeminiSummarizerAdapter
from src.infrastructure.external_api.rss_adapter import RssNewsSource # Asumiendo que usamos RSS como default para MVP

# Aplicación (Servicios & Handlers)
from src.application.commands.create_preference import CreatePreferenceHandler
from src.application.commands.generate_briefing import GenerateDailyBriefingHandler
from src.application.services.news_fetcher_service import NewsFetcherService
from src.application.interfaces.ai_service import AISummarizerService
from src.application.interfaces.notification_service import NotificationService
from src.infrastructure.external_api.email_adapter import EmailNotificationAdapter

# --- Repositorios ---

def get_preference_repo(session: AsyncSession = Depends(get_session)) -> SqlAlchemyPreferenceRepository:
    return SqlAlchemyPreferenceRepository(session=session)

def get_briefing_repo(session: AsyncSession = Depends(get_session)) -> SqlAlchemyBriefingRepository:
    return SqlAlchemyBriefingRepository(session=session)

# --- Servicios Externos (Strategies/Adapters) ---

def get_ai_service() -> AISummarizerService:
    """Inyecta el adapter de IA (Gemini)."""
    return GeminiSummarizerAdapter()

def get_news_source() -> RssNewsSource:
    """
    Inyecta la fuente de noticias por defecto. 
    En un sistema avanzado, esto podría ser una Factory basada en la config del usuario.
    Para el MVP, usamos un feed de tecnología genérico o inyectamos la URL desde env vars.
    """
    # Ejemplo: Feed de HackerNews o TechCrunch
    return RssNewsSource(feed_url="https://feeds.feedburner.com/TechCrunch/")

def get_news_fetcher_service(
    source: RssNewsSource = Depends(get_news_source)
) -> NewsFetcherService:
    return NewsFetcherService(source=source)

def get_notification_service() -> NotificationService:
    return EmailNotificationAdapter()

# --- Handlers (Casos de Uso) ---

def get_create_preference_handler(
    repo: SqlAlchemyPreferenceRepository = Depends(get_preference_repo)
) -> CreatePreferenceHandler:
    return CreatePreferenceHandler(repo=repo)

def get_generate_briefing_handler(
    pref_repo: SqlAlchemyPreferenceRepository = Depends(get_preference_repo),
    briefing_repo: SqlAlchemyBriefingRepository = Depends(get_briefing_repo),
    news_service: NewsFetcherService = Depends(get_news_fetcher_service),
    ai_service: AISummarizerService = Depends(get_ai_service),
    notification_service: NotificationService = Depends(get_notification_service)
) -> GenerateDailyBriefingHandler:
    return GenerateDailyBriefingHandler(
        pref_repo=pref_repo,
        briefing_repo=briefing_repo,
        news_service=news_service,
        ai_service=ai_service,
        notification_service=notification_service
    )