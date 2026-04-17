from typing import List
from datetime import datetime
from src.domain.repositories.news_source_repository import NewsSourceRepository
from src.domain.models.news_item import NewsItem

class MockNewsSource(NewsSourceRepository):
    async def fetch_news(self, topic: str, limit: int = 5) -> List[NewsItem]:
        return [
            NewsItem(
                title=f"Noticia Mock sobre {topic} 1",
                url="http://mock.com/1",
                summary_raw="Contenido de prueba 1",
                published_at=datetime.now(),
                source_name="Mock Source"
            ),
            NewsItem(
                title=f"Noticia Mock sobre {topic} 2",
                url="http://mock.com/2",
                summary_raw="Contenido de prueba 2",
                published_at=datetime.now(),
                source_name="Mock Source"
            )
        ]