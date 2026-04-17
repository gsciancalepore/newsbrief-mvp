from google import genai
from typing import List
import os
import asyncio
from src.application.interfaces.ai_service import AISummarizerService

class GeminiSummarizerAdapter(AISummarizerService):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY no configurada")
        
        # --- CAMBIO CLAVE: Nueva forma de inicializar el cliente ---
        self.client = genai.Client(api_key=self.api_key)
        self.model_id = 'gemini-1.5-flash'

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
            # --- CAMBIO CLAVE: Nueva forma de llamar al modelo asíncronamente ---
            # El nuevo SDK usa models.generate_content
            response = await self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            return response.text
        except Exception as e:
            raise Exception(f"Error al llamar a Gemini API: {str(e)}")