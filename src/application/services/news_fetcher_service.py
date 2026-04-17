from typing import List
from src.domain.repositories.news_source_repository import NewsSourceRepository
from src.domain.models.news_item import NewsItem

class NewsFetcherService:
    def __init__(self, source: NewsSourceRepository):
        self.source = source

    async def get_latest_news(self, topic: str, limit: int = 5) -> List[NewsItem]:
        """
        Delega la obtención de noticias a la estrategia configurada.
        """
        return await self.source.fetch_news(topic=topic, limit=limit)