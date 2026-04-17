import pytest
from uuid import uuid4
from src.infrastructure.database.repositories import SqlAlchemyPreferenceRepository, SqlAlchemyBriefingRepository
from src.application.commands.generate_briefing import GenerateDailyBriefingCommand, GenerateDailyBriefingHandler
from src.application.commands.create_preference import CreatePreferenceCommand, CreatePreferenceHandler
from src.application.services.news_fetcher_service import NewsFetcherService
from src.application.interfaces.notification_service import NotificationService
from tests.mocks.news_source_mock import MockNewsSource
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_integration_generate_briefing_saves_to_db(db_session):
    # 1. Setup: Usar la sesión inyectada directamente
    user_id = uuid4()

    pref_repo = SqlAlchemyPreferenceRepository(db_session)
    create_pref_handler = CreatePreferenceHandler(repo=pref_repo)
    test_pref = await create_pref_handler.execute(
        CreatePreferenceCommand(
            user_id=user_id,
            topic_str="tecnologia",
            tone_str="formal"
        )
    )

    # 2. Configurar Handler con la misma sesión
    news_service = NewsFetcherService(source=MockNewsSource())
    mock_ai = AsyncMock()
    mock_ai.summarize_news.return_value = "Resumen Mock"
    
    # Mock del servicio de notificación
    mock_notification = AsyncMock(spec=NotificationService)
    mock_notification.send_summary.return_value = True

    handler = GenerateDailyBriefingHandler(
        pref_repo=pref_repo,
        briefing_repo=SqlAlchemyBriefingRepository(db_session),
        news_service=news_service,
        ai_service=mock_ai,
        notification_service=mock_notification
    )

    # 3. Ejecutar
    command = GenerateDailyBriefingCommand(
        user_id=user_id,
        recipient_email="test@example.com"
    )

    briefing = await handler.execute(command)

    # 4. Asserts
    assert briefing.status.value == "COMPLETED"
    assert len(briefing.items) > 0

    # Verificar persistencia en la misma sesión
    saved = await SqlAlchemyBriefingRepository(db_session).get_by_id(briefing.id)
    assert saved is not None
    assert saved.status.value == "COMPLETED"
    
    # Verificar que el servicio de notificación fue llamado con los parámetros correctos
    mock_notification.send_summary.assert_called_once_with(
        recipient="test@example.com",
        summary_text="Resumen Mock"
    )