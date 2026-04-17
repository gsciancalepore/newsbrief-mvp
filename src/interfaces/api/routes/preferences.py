from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.interfaces.schemas.preference import CreatePreferenceRequest, PreferenceResponse
from src.application.commands.create_preference import CreatePreferenceCommand, CreatePreferenceHandler
from src.interfaces.api.dependencies import get_create_preference_handler
from src.infrastructure.database.config import get_session

router = APIRouter(prefix="/preferences", tags=["Preferences"])

@router.post("/", response_model=PreferenceResponse, status_code=status.HTTP_201_CREATED)
async def create_preference(
    request: CreatePreferenceRequest,
    handler: CreatePreferenceHandler = Depends(get_create_preference_handler),
    session: AsyncSession = Depends(get_session),
    # En un sistema real, user_id vendría del token JWT. Hardcodeamos para MVP.
    current_user_id: UUID = UUID("123e4567-e89b-12d3-a456-426614174000") 
):
    try:
        # 1. Crear el Comando de Aplicación
        command = CreatePreferenceCommand(
            user_id=current_user_id,
            topic_str=request.topic,
            tone_str=request.tone.value
        )
        
        # 2. Ejecutar Caso de Uso
        preference = await handler.execute(command)
        
        # 3. Commit de la transacción
        await session.commit()
        
        # 4. Retornar Respuesta
        return PreferenceResponse(
            id=preference.id,
            user_id=preference.user_id,
            topic=preference.topic.value,
            tone=preference.tone,
            is_active=preference.is_active
        )
        
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")