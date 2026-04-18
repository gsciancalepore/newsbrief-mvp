from dataclasses import dataclass
import logging
from uuid import UUID
from typing import List
from src.domain.models.briefing import Briefing, BriefingStatus
from src.domain.repositories.preference_repository import PreferenceRepository
from src.domain.repositories.briefing_repository import BriefingRepository
from src.application.services.news_fetcher_service import NewsFetcherService
from src.domain.models.news_item import NewsItem
from src.application.interfaces.ai_service import AISummarizerService
from src.application.interfaces.notification_service import NotificationService

logger = logging.getLogger(__name__)

@dataclass
class GenerateDailyBriefingCommand:
    user_id: UUID
    recipient_email: str

class GenerateDailyBriefingHandler:
    def __init__(
        self, 
        pref_repo: PreferenceRepository,
        briefing_repo: BriefingRepository,
        news_service: NewsFetcherService,
        ai_service: AISummarizerService,
        notification_service: NotificationService
    ):
        self.pref_repo = pref_repo
        self.briefing_repo = briefing_repo
        self.news_service = news_service
        self.ai_service = ai_service
        self.notification_service = notification_service

    async def execute(self, command: GenerateDailyBriefingCommand) -> Briefing:
        logger.info(f"Starting briefing generation for user {command.user_id}")

        latest = await self.briefing_repo.get_latest_completed(command.user_id, hours=24)
        if latest:
            logger.info(f"Briefing already generated in last 24h for user {command.user_id}. Skipping.")
            return latest

        preferences = await self.pref_repo.get_by_user_id(command.user_id)
        
        if not preferences:
            raise ValueError("El usuario no tiene preferencias configuradas.")

        logger.info(f"Fetching news for topics: {[p.topic.value for p in preferences]}")

        briefing = Briefing(user_id=command.user_id)

        all_news_items: List[NewsItem] = []
        
        for pref in preferences:
            items = await self.news_service.get_latest_news(
                topic=pref.topic.value, 
                limit=3
            )
            all_news_items.extend(items)

        all_news_dicts = [
            {"title": item.title, "summary_raw": item.summary_raw} 
            for item in all_news_items
        ]
        
        default_tone = preferences[0].tone.value if preferences else "formal"
        
        logger.info(f"Summarizing {len(all_news_dicts)} news items with tone '{default_tone}' via AI...")
        
        summary_text = await self.ai_service.summarize_news(
            news_items=all_news_dicts, 
            tone=default_tone
        )

        briefing.add_item({
            "title": f"Resumen Diario ({default_tone})",
            "content": summary_text,
            "source": "Gemini AI"
        })
        
        briefing.mark_as_completed()
        
        logger.info(f"Saving briefing to DB (status={briefing.status})")
        await self.briefing_repo.save(briefing)
        
        if briefing.status == BriefingStatus.COMPLETED:
            summary_content = briefing.items[0].get('content', 'Sin resumen disponible.') if briefing.items else "Sin contenido."
            logger.info(f"Sending email notification to {command.recipient_email}...")
            await self.notification_service.send_summary(
                recipient=command.recipient_email,
                summary_text=summary_content
            )
        
        logger.info(f"Briefing completed for user {command.user_id}")
        return briefing