from uuid import UUID, uuid4
from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict, Any

class BriefingStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Briefing:
    def __init__(self, user_id: UUID, briefing_id: UUID = None, status: BriefingStatus = BriefingStatus.PENDING):
        self.id = briefing_id or uuid4() # En producción, esto se genera al guardar o se inyecta. Para tests, podemos dejarlo mutable o usar factory.
        # Nota: Para mantener pureza en DDD, a veces el ID se asigna en el repositorio. 
        # Para simplificar este MVP, asumiremos que el ID se puede setear o generar aquí si es necesario.
        # Vamos a mejorar esto: El ID debería ser inmutable una vez creado.
        
        self.user_id = user_id
        self.status = status
        self.created_at = datetime.now(timezone.utc)
        self._items: List[Dict[str, Any]] = []

    @property
    def items(self) -> List[Dict[str, Any]]:
        return list(self._items) # Retornamos copia para inmutabilidad externa

    def add_item(self, item: Dict[str, Any]):
        if self.status != BriefingStatus.PENDING:
            raise Exception("No se pueden agregar items a un briefing completado o fallido.")
        self._items.append(item)

    def mark_as_completed(self):
        if not self._items:
            raise ValueError("No se puede completar un briefing vacío.")
        self.status = BriefingStatus.COMPLETED

    def mark_as_failed(self):
        self.status = BriefingStatus.FAILED

    def __repr__(self):
        return f"Briefing(user_id={self.user_id}, status={self.status}, items_count={len(self._items)})"