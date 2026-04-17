from abc import ABC, abstractmethod
from typing import List
from src.domain.models.news_item import NewsItem

class NewsSourceRepository(ABC):
    """
    Interfaz para cualquier fuente de noticias (RSS, API, Scraper).
    Implementa el patrón Strategy.
    """
    
    @abstractmethod
    async def fetch_news(self, topic: str, limit: int = 5) -> List[NewsItem]:
        """
        Obtiene noticias relacionadas con un tópico.
        """
        pass