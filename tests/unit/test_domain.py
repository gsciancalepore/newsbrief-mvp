import pytest
from uuid import uuid4
from datetime import datetime
# Ajusta las importaciones según tu estructura final
from src.domain.value_objects.email import Email
from src.domain.models.user import User
from src.domain.models.briefing import Briefing, BriefingStatus
from src.domain.value_objects.topic import Topic
from src.domain.value_objects.tone import Tone
from src.domain.models.preference import UserPreference

def test_email_value_object_valid():
    """Un email válido debe crearse sin errores."""
    email = Email("gabbb@example.com")
    assert email.value == "gabbb@example.com"

def test_email_value_object_invalid():
    """Un email inválido debe lanzar una excepción."""
    with pytest.raises(ValueError):
        Email("no-es-un-email")

def test_user_creation():
    """Un usuario debe crearse con un ID y email válido."""
    user_id = uuid4()
    email = Email("gabbb@example.com")
    user = User(id=user_id, email=email)
    
    assert user.id == user_id
    assert user.email == email
    assert user.is_active is True # Por defecto activo

def test_briefing_creation():
    """Un briefing debe iniciarse en estado PENDING."""
    user_id = uuid4()
    briefing = Briefing(user_id=user_id)
    
    assert briefing.user_id == user_id
    assert briefing.status == BriefingStatus.PENDING
    assert briefing.id is not None # Ahora tiene ID propio
    assert isinstance(briefing.created_at, datetime)
    assert len(briefing.items) == 0

def test_briefing_add_item():
    """Agregar un item al briefing debe aumentar la lista."""
    user_id = uuid4()
    briefing = Briefing(user_id=user_id)
    
    # Simulamos un item de noticia (podría ser otro VO o Entidad simple)
    news_item = {"title": "Noticia Test", "url": "http://test.com"}
    briefing.add_item(news_item)
    
    assert len(briefing.items) == 1
    assert briefing.items[0] == news_item

# --- Tests para Value Objects ---

def test_topic_creation_valid():
    """Un tópico válido debe crearse y normalizarse (minúsculas)."""
    topic = Topic("Artificial Intelligence")
    assert topic.value == "artificial intelligence"

def test_topic_creation_invalid_empty():
    """Un tópico vacío debe fallar."""
    with pytest.raises(ValueError):
        Topic("")

def test_tone_enum_values():
    """Los tonos deben ser predefinidos."""
    assert Tone.FORMAL.value == "formal"
    assert Tone.INFORMAL.value == "informal"
    assert Tone.SARCASTIC.value == "sarcastic"

# --- Tests para Entidad Preference ---

def test_preference_creation():
    """Una preferencia une un Usuario, un Tópico y un Tono."""
    user_id = uuid4()
    topic = Topic("Python")
    tone = Tone.FORMAL
    
    pref = UserPreference(user_id=user_id, topic=topic, tone=tone)
    
    assert pref.user_id == user_id
    assert pref.topic == topic
    assert pref.tone == tone
    assert pref.is_active is True

def test_preference_update_tone():
    """El usuario puede cambiar el tono de su preferencia."""
    user_id = uuid4()
    topic = Topic("Python")
    pref = UserPreference(user_id=user_id, topic=topic, tone=Tone.FORMAL)
    
    pref.update_tone(Tone.INFORMAL)
    assert pref.tone == Tone.INFORMAL