import pytest
from uuid import uuid4
from unittest.mock import AsyncMock
from src.application.commands.create_preference import CreatePreferenceCommand, CreatePreferenceHandler
from src.domain.value_objects.tone import Tone

@pytest.mark.asyncio
async def test_create_preference_handler_success():
    # 1. Preparar Dependencias (Mock del Repositorio)
    mock_repo = AsyncMock()
    handler = CreatePreferenceHandler(repo=mock_repo)

    # 2. Preparar Comando
    user_id = uuid4()
    command = CreatePreferenceCommand(
        user_id=user_id,
        topic_str="Artificial Intelligence",
        tone_str="Formal"
    )

    # 3. Ejecutar
    result = await handler.execute(command)

    # 4. Verificar
    assert result.topic.value == "artificial intelligence"
    assert result.tone == Tone.FORMAL
    assert result.user_id == user_id
    
    # Verificar que el repositorio fue llamado
    mock_repo.save.assert_called_once_with(result)

@pytest.mark.asyncio
async def test_create_preference_handler_invalid_tone():
    mock_repo = AsyncMock()
    handler = CreatePreferenceHandler(repo=mock_repo)

    command = CreatePreferenceCommand(
        user_id=uuid4(),
        topic_str="Python",
        tone_str="Gritando" # Tono inválido
    )

    with pytest.raises(ValueError):
        await handler.execute(command)
        
    # El repositorio NO debe ser llamado si falla la validación
    mock_repo.save.assert_not_called()