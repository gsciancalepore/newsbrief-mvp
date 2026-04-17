from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from src.infrastructure.database.base import Base
from src.domain.value_objects.tone import Tone # Importamos el Enum de dominio
from src.domain.models.briefing import BriefingStatus

class UserPreferenceModel(Base):
    __tablename__ = "user_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Mapeo de Value Objects a columnas
    topic = Column(String, nullable=False) 
    tone = Column(SQLEnum(Tone), nullable=False, default=Tone.FORMAL)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<UserPreference(id={self.id}, topic={self.topic})>"

class BriefingModel(Base):
    __tablename__ = "briefings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    status = Column(SQLEnum(BriefingStatus), nullable=False, default=BriefingStatus.PENDING)
    # Guardamos los items como JSONB para flexibilidad en el MVP
    items = Column(JSON, default=list) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())