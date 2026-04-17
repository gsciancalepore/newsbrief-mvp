import pytest
from unittest.mock import patch, AsyncMock
from uuid import uuid4
from src.infrastructure.celery.tasks import generate_daily_briefing_task

@pytest.mark.asyncio
async def test_generate_daily_briefing_task_calls_handler():
    user_id = uuid4()
    
    # Mockeamos el handler completo para no ejecutar la lógica real
    with patch('src.infrastructure.celery.tasks.GenerateDailyBriefingHandler') as MockHandler:
        mock_instance = AsyncMock()
        MockHandler.return_value = mock_instance
        
        # Ejecutamos la tarea (que internamente corre el event loop)
        # Nota: Como la tarea usa asyncio.run(), la llamamos directamente
        from src.infrastructure.celery.tasks import _process_briefing
        await _process_briefing(user_id)
        
        # Verificamos que el handler se haya ejecutado
        assert mock_instance.execute.called
