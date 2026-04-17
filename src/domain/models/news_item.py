from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class NewsItem:
    title: str
    url: str
    summary_raw: str # Contenido crudo o resumen inicial
    published_at: datetime
    source_name: str
    
    def __post_init__(self):
        if not self.title or not self.url:
            raise ValueError("Title and URL are required")