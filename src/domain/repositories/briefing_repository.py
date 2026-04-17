from abc import ABC, abstractmethod
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