from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Optional
from uuid import UUID
from src.domain.models.briefing import Briefing

class BriefingRepository(ABC):

    @abstractmethod
    async def save(self, briefing: Briefing) -> None:
        """Persiste el briefing generado."""
        pass

    @abstractmethod
    async def get_by_id(self, briefing_id: UUID) -> Optional[Briefing]:
        """Obtiene un briefing por su ID."""
        pass

    @abstractmethod
    async def get_latest_completed(self, user_id: UUID, hours: int = 24) -> Optional[Briefing]:
        """Obtiene el último briefing completado para un usuario dentro de las últimas N horas."""
        pass