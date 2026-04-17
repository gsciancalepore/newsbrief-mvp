from dataclasses import dataclass
from uuid import UUID
from src.domain.value_objects.topic import Topic
from src.domain.value_objects.tone import Tone
from src.domain.models.preference import UserPreference
from src.domain.repositories.preference_repository import PreferenceRepository

@dataclass
class CreatePreferenceCommand:
    user_id: UUID
    topic_str: str  # Recibimos string crudo, el caso de uso lo valida
    tone_str: str   # Recibimos string crudo

class CreatePreferenceHandler:
    def __init__(self, repo: PreferenceRepository):
        self.repo = repo

    async def execute(self, command: CreatePreferenceCommand) -> UserPreference:
        # 1. Validar y convertir Value Objects (Reglas de Dominio)
        try:
            topic = Topic(command.topic_str)
            tone = Tone(command.tone_str.lower())
        except ValueError as e:
            raise ValueError(f"Datos de entrada inválidos: {e}")

        # 2. Crear la Entidad de Dominio
        new_preference = UserPreference(
            user_id=command.user_id,
            topic=topic,
            tone=tone
        )

        # 3. Persistir usando el Puerto (Abstracción)
        await self.repo.save(new_preference)

        # 4. Retornar la entidad (o un DTO de salida)
        return new_preference