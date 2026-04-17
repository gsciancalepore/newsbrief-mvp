from uuid import UUID, uuid4
from src.domain.value_objects.topic import Topic
from src.domain.value_objects.tone import Tone

class UserPreference:
    def __init__(self, user_id: UUID, topic: Topic, tone: Tone = Tone.FORMAL, is_active: bool = True, id: UUID = None):
        self.id = id or uuid4()
        self.user_id = user_id
        self.topic = topic
        self.tone = tone
        self.is_active = is_active

    def update_tone(self, new_tone: Tone):
        """Cambia el estilo de resumen para este tópico."""
        self.tone = new_tone

    def deactivate(self):
        """Desuscribe al usuario de este tópico."""
        self.is_active = False

    def activate(self):
        self.is_active = True

    def __repr__(self):
        return f"Pref(user={self.user_id}, topic={self.topic}, tone={self.tone})"