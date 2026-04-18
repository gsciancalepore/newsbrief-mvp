from google import genai
from google.genai import types
from typing import List
import os
from src.application.interfaces.ai_service import AISummarizerService

class GeminiSummarizerAdapter(AISummarizerService):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY no configurada")
        
        # Cliente sync base
        self.client = genai.Client(
            api_key=self.api_key,
            http_options=types.HttpOptions(api_version='v1')
        )
        # Cliente async nativo (no bloquea event loop)
        self.async_client = self.client.aio
        self.model_id = 'gemini-2.5-flash-lite'

    async def summarize_news(self, news_items: List[dict], tone: str, language: str = "es") -> str:
        """
        Genera un resumen basado en el tono y lenguaje solicitados usando el nuevo SDK.
        """
        news_text = "\n".join([f"- {item['title']}: {item.get('summary_raw', '')}" for item in news_items])
        
        prompt = f"""
        Actúa como un editor de noticias experto.
        Resume las siguientes noticias en un solo bloque coherente.
        
        Idioma: {language}
        Tono: {tone} (Si es 'informal', usa un lenguaje cercano; si es 'formal', sé profesional).
        
        Noticias:
        {news_text}
        
        Formato de salida:
        Un párrafo introductorio breve y luego los puntos clave resumidos.
        """

        try:
            response = await self.async_client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            return response.text
        except Exception as e:
            raise Exception(f"Error al llamar a Gemini API: {str(e)}")