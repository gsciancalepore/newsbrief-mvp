from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from src.domain.value_objects.tone import Tone

class CreatePreferenceRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=50, description="Tema de interés")
    tone: Tone = Field(default=Tone.FORMAL, description="Estilo del resumen")

class PreferenceResponse(BaseModel):
    id: UUID
    user_id: UUID
    topic: str
    tone: Tone
    is_active: bool

    class Config:
        from_attributes = True # Para mapear desde ORM o Entidades fácilmente