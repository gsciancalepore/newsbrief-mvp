from abc import ABC, abstractmethod
from typing import List

class AISummarizerService(ABC):
    
    @abstractmethod
    async def summarize_news(self, news_items: List[dict], tone: str, language: str = "es") -> str:
        """
        Recibe una lista de noticias crudas y devuelve un resumen estructurado.
        """
        pass