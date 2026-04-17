from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.preference import UserPreference
from src.domain.repositories.preference_repository import PreferenceRepository
from src.domain.value_objects.topic import Topic
from src.domain.value_objects.tone import Tone

from src.domain.models.briefing import Briefing, BriefingStatus
from src.domain.repositories.briefing_repository import BriefingRepository

from src.infrastructure.database.models import UserPreferenceModel, BriefingModel


class SqlAlchemyPreferenceRepository(PreferenceRepository):
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, preference: UserPreference) -> None:

        # 1. Mapear Dominio -> ORM
        db_pref = UserPreferenceModel(
            id=preference.id if preference.id.int != 0 else None, 
            user_id=preference.user_id,
            topic=preference.topic.value,
            tone=preference.tone,
            is_active=preference.is_active
        )

        self.session.add(db_pref)
        await self.session.flush()
        await self.session.refresh(db_pref)
        
        # Actualizar el ID de la entidad de dominio si era nuevo
        if preference.id.int == 0:
            preference.id = db_pref.id

    async def get_by_user_id(self, user_id: UUID) -> List[UserPreference]:
        result = await self.session.execute(
            select(UserPreferenceModel).where(
                UserPreferenceModel.user_id == user_id,
                UserPreferenceModel.is_active == True
            )
        )
        db_prefs = result.scalars().all()
        
        return [
            UserPreference(
                id=db_p.id,
                user_id=db_p.user_id,
                topic=Topic(db_p.topic),
                tone=db_p.tone,
                is_active=db_p.is_active
            )
            for db_p in db_prefs
        ]

    async def get_by_id(self, preference_id: UUID) -> Optional[UserPreference]:
        result = await self.session.execute(
            select(UserPreferenceModel).where(UserPreferenceModel.id == preference_id)
        )
        db_pref = result.scalar_one_or_none()
        
        if not db_pref:
            return None
            
        return UserPreference(
            id=db_pref.id,
            user_id=db_pref.user_id,
            topic=Topic(db_pref.topic),
            tone=db_pref.tone,
            is_active=db_pref.is_active
        )


class SqlAlchemyBriefingRepository(BriefingRepository):
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, briefing: Briefing) -> None:
        # Mapear Entidad -> ORM
        db_briefing = BriefingModel(
            id=briefing.id if briefing.id else None,
            user_id=briefing.user_id,
            status=briefing.status,
            items=briefing.items, 
            created_at=briefing.created_at
        )
        
        self.session.add(db_briefing)
        await self.session.flush()
        await self.session.refresh(db_briefing)
        
        # Sincronizar ID si era nuevo
        if not briefing.id:
             briefing.id = db_briefing.id

    async def get_by_id(self, briefing_id: UUID) -> Optional[Briefing]:
        result = await self.session.execute(
            select(BriefingModel).where(BriefingModel.id == briefing_id)
        )
        db_briefing = result.scalar_one_or_none()
        
        if not db_briefing:
            return None
            
        # Reconstruir la entidad de dominio
        briefing = Briefing(user_id=db_briefing.user_id)
        briefing.id = db_briefing.id
        briefing.status = db_briefing.status
        briefing.created_at = db_briefing.created_at
        
        # Restaurar items manualmente (accediendo al atributo protegido para reconstrucción)
        briefing._items = db_briefing.items or []
        
        return briefing