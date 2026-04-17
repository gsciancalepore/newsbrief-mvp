from abc import ABC, abstractmethod

class NotificationService(ABC):
    @abstractmethod
    async def send_summary(self, recipient: str, summary_text: str) -> bool:
        """
        Envía el resumen generado al destinatario.
        Retorna True si fue exitoso.
        """
        pass