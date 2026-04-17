from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from src.domain.models.preference import UserPreference

class PreferenceRepository(ABC):
    
    @abstractmethod
    async def save(self, preference: UserPreference) -> None:
        """Persiste una nueva preferencia o actualiza una existente."""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> List[UserPreference]:
        """Obtiene todas las preferencias activas de un usuario."""
        pass

    @abstractmethod
    async def get_by_id(self, preference_id: UUID) -> Optional[UserPreference]:
        """Obtiene una preferencia específica por su ID."""
        pass