import pytest
from uuid import uuid4
from unittest.mock import AsyncMock
from src.application.commands.generate_briefing import GenerateDailyBriefingCommand, GenerateDailyBriefingHandler
from src.domain.models.preference import UserPreference
from src.domain.value_objects.topic import Topic
from src.domain.value_objects.tone import Tone
from src.application.services.news_fetcher_service import NewsFetcherService
from src.domain.models.news_item import NewsItem
from src.application.interfaces.ai_service import AISummarizerService
from src.application.interfaces.notification_service import NotificationService
from datetime import datetime

@pytest.mark.asyncio
async def test_generate_briefing_uses_strategy(mock_briefing_repo):
    # Mocks
    mock_pref_repo = AsyncMock()
    # mock_briefing_repo viene del fixture en conftest.py
    
    # Configurar preferencia mock
    user_id = uuid4()
    pref = UserPreference(user_id=user_id, topic=Topic("Python"), tone=Tone.FORMAL)
    mock_pref_repo.get_by_user_id.return_value = [pref]

    # Configurar Strategy Mock (Simulamos una fuente RSS)
    mock_news_source = AsyncMock()
    mock_news_source.fetch_news.return_value = [
        NewsItem(title="PyCon 2026", url="http://pycon.com", summary_raw="...", published_at=datetime.now(), source_name="PyCon")
    ]
    
    news_service = NewsFetcherService(source=mock_news_source)

    # Mock del servicio de IA
    mock_ai_service = AsyncMock()
    mock_ai_service.summarize_news.return_value = "Resumen de prueba de noticias sobre Python en tono formal"
    
    # Mock del servicio de notificación
    mock_notification = AsyncMock(spec=NotificationService)
    mock_notification.send_summary.return_value = True

    # Handler
    handler = GenerateDailyBriefingHandler(
        pref_repo=mock_pref_repo,
        briefing_repo=mock_briefing_repo,
        news_service=news_service,
        ai_service=mock_ai_service,
        notification_service=mock_notification
    )

    # Ejecutar
    command = GenerateDailyBriefingCommand(
        user_id=user_id,
        recipient_email="test@example.com"
    )
    briefing = await handler.execute(command)

    # Verificar
    assert len(briefing.items) == 1
    assert briefing.items[0]['title'] == "Resumen Diario (formal)"
    assert briefing.items[0]['content'] == "Resumen de prueba de noticias sobre Python en tono formal"
    assert briefing.items[0]['source'] == "Gemini AI"
    
    # Verificar que se llamó a la estrategia correcta
    mock_news_source.fetch_news.assert_called_once_with(topic="python", limit=3)