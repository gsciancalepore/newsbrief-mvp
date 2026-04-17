import feedparser
from typing import List
from datetime import datetime
from src.domain.repositories.news_source_repository import NewsSourceRepository
from src.domain.models.news_item import NewsItem

class RssNewsSource(NewsSourceRepository):
    def __init__(self, feed_url: str):
        self.feed_url = feed_url

    async def fetch_news(self, topic: str, limit: int = 5) -> List[NewsItem]:
        """
        Nota: RSS no suele permitir filtrar por 'topic' nativamente 
        a menos que el feed sea específico. 
        Para este MVP, asumimos que el feed_url YA es específico del tema 
        (ej. feed de 'Tech' de HackerNews).
        """
        feed = feedparser.parse(self.feed_url)
        items = []
        
        for entry in feed.entries[:limit]:
            # Normalización de datos
            pub_date = datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now()
            
            news_item = NewsItem(
                title=entry.title,
                url=entry.link,
                summary_raw=entry.get('summary', entry.get('description', '')),
                published_at=pub_date,
                source_name=feed.feed.get('title', 'RSS Source')
            )
            items.append(news_item)
            
        return items