# newsbrief Architecture - C4 Level 1

```mermaid
C4Context
    title Sistema NewsBrief MVP - C4 Level 1 (Contexto)

    Person(usuario, "Usuario Final", "Suscriptor que configura preferencias y recibe resúmenes diarios.")
    
    System_Boundary(newsbrief, "NewsBrief System") {
        System(api, "NewsBrief API", "FastAPI", "Gestión de usuarios, preferencias y consulta de historial.")
        System(worker, "News Processor", "Celery Worker", "Orquestación: Búsqueda, Resumen IA y Notificación.")
        SystemDb(db, "PostgreSQL", "SQL Database", "Persistencia de entidades de dominio (User, Briefing, Preference).")
        SystemQueue(queue, "Redis", "Message Broker", "Cola de tareas asíncronas y caché.")
    }

    System_Ext(gemini, "Google Gemini API", "AI Service", "Generación de resúmenes con tono personalizado (LLM).")
    System_Ext(rss, "RSS Feeds", "External Data", "Fuentes de noticias crudas (TechCrunch, etc.).")
    System_Ext(smtp, "SMTP Server", "Email Provider", "Envío de notificaciones (Gmail/SendGrid).")

    Rel(usuario, api, "HTTPS/REST", "Configura temas y tonos")
    Rel(usuario, smtp, "Recepción Pasiva", "Recibe email diario")
    
    Rel(api, queue, "Push Task", "Encola 'GenerateBriefing'")
    Rel(worker, queue, "Pop Task", "Consume tareas pendientes")
    
    Rel(worker, db, "SQL (AsyncPG)", "Lee prefs / Guarda briefing")
    Rel(worker, rss, "HTTP GET", "Obtiene noticias crudas")
    Rel(worker, gemini, "HTTPS/API", "Solicita resumen estructurado")
    Rel(worker, smtp, "SMTP", "Envía resultado final")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

## Descripción del Diagrama

### Actores
- **Usuario Final**: Persona que usa la API REST y recibe emails con los briefings

### Sistemas Internos (NewsBrief MVP)
- **API REST** (FastAPI): Expone endpoints para gestión de preferencias
- **Celery Worker**: Procesa tareas asíncronas de generación de briefings
- **PostgreSQL**: Almacena usuarios, preferencias y briefings
- **Redis**: Broker de mensajes y cache

### Sistemas Externos
- **Gemini API**: Servicio de IA para generar resúmenes
- **RSS Feeds**: Fuentes de noticias técnicas
- **Servidor SMTP**: Envío de emails

### Relaciones Principales
| De | A | Protocolo | Descripción |
|---|---|---|---|
| Usuario | NewsBrief API | HTTPS/REST | Configura temas, tonos y consulta historial |
| Usuario | SMTP Server | SMTP (Pasivo) | Recibe el email con el resumen diario |
| NewsBrief API | Redis | TCP/IP (Push) | Encola la tarea GenerateBriefing |
| Celery Worker | Redis | TCP/IP (Pop) | Consume tareas pendientes de la cola |
| Celery Worker | PostgreSQL | SQL (AsyncPG) | Lee preferencias y guarda el briefing generado |
| Celery Worker | RSS Feeds | HTTP GET | Obtiene las noticias crudas del día |
| Celery Worker | Google Gemini | HTTPS/API | Solicita el resumen estructurado con tono |
| Celery Worker | SMTP Server | SMTP | Envía el resultado final al usuario |