from dataclasses import dataclass
from uuid import UUID
from typing import List
from src.domain.models.briefing import Briefing, BriefingStatus
from src.domain.repositories.preference_repository import PreferenceRepository
from src.domain.repositories.briefing_repository import BriefingRepository
from src.application.services.news_fetcher_service import NewsFetcherService
from src.domain.models.news_item import NewsItem
from src.application.interfaces.ai_service import AISummarizerService
from src.application.interfaces.notification_service import NotificationService

@dataclass
class GenerateDailyBriefingCommand:
    user_id: UUID
    recipient_email: str # Agregamos el destino para enviar el resumen

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
        # 1. Obtener preferencias activas
        preferences = await self.pref_repo.get_by_user_id(command.user_id)
        
        if not preferences:
            raise ValueError("El usuario no tiene preferencias configuradas.")

        # 2. Crear el agregado Briefing
        briefing = Briefing(user_id=command.user_id)

        # 3. Por cada preferencia, buscar noticias
        all_news_items: List[NewsItem] = []
        
        for pref in preferences:
            # Aquí usamos el Strategy Pattern inyectado
            items = await self.news_service.get_latest_news(
                topic=pref.topic.value, 
                limit=3 # Traemos 3 por tema
            )
            all_news_items.extend(items)

        # 4. Agregar items al briefing (Transformación simple para MVP)
        # Agrupamos las noticias para enviarlas a Gemini
        all_news_dicts = [
            {"title": item.title, "summary_raw": item.summary_raw} 
            for item in all_news_items
        ]
        
        # Obtenemos el tono de la primera preferencia (o promediamos, según lógica de negocio)
        default_tone = preferences[0].tone.value if preferences else "formal"
        
        try:
            summary_text = await self.ai_service.summarize_news(
                news_items=all_news_dicts, 
                tone=default_tone
            )
        except Exception as e:
            briefing.mark_as_failed()
            # Loguear error...
            await self.briefing_repo.save(briefing)
            return briefing

        # 5. Marcar como completado (En un flujo real, aquí iría la llamada a IA)
        briefing.add_item({
            "title": f"Resumen Diario ({default_tone})",
            "content": summary_text, # Aquí guardamos el resumen de IA
            "source": "Gemini AI"
        })
        
        briefing.mark_as_completed()
        await self.briefing_repo.save(briefing)
        
        # 7. Enviar notificación por email
        if briefing.status == BriefingStatus.COMPLETED:
            summary_content = briefing.items[0].get('content', 'Sin resumen disponible.') if briefing.items else "Sin contenido."
            await self.notification_service.send_summary(
                recipient=command.recipient_email,
                summary_text=summary_content
            )
        
        return briefing