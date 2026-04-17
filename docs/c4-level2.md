# NewsBrief MVP - C4 Level 2 (Containers)

```mermaid
C4Container
    title Sistema NewsBrief MVP - C4 Level 2 (Contenedores)

    Person(usuario, "Usuario Final", "Gestiona preferencias y recibe resúmenes")

    Container_Boundary(app_boundary, "Aplicación Web (API)") {
        Container(api_app, "NewsBrief API", "Python, FastAPI, Uvicorn", "Expone endpoints REST y valida requests.")
    }

    Container_Boundary(worker_boundary, "Procesador Asíncrono") {
        Container(worker_app, "Celery Worker", "Python, Celery", "Ejecuta tareas pesadas: Fetch, IA, Notify.")
        Container(beat_app, "Celery Beat", "Python, Celery", "Scheduler que dispara tareas periódicas.")
    }

    Container_Boundary(infra_boundary, "Infraestructura de Datos") {
        ContainerDb(db, "PostgreSQL", "PostgreSQL 16", "Persistencia de Dominio (Users, Briefings).")
        ContainerQueue(queue, "Redis", "Redis 7", "Message Broker para tareas Celery.")
    }

    System_Ext(gemini, "Google Gemini API", "LLM Service", "Generación de resúmenes con tono.")
    System_Ext(rss, "RSS Feeds", "External Data", "Fuentes de noticias (TechCrunch, etc.).")
    System_Ext(smtp, "SMTP Server", "Email Service", "Envío de notificaciones (Gmail/SendGrid).")

    Rel(usuario, api_app, "HTTPS/REST", "1. Configura preferencias")
    
    Rel(api_app, queue, "Push Task", "2. Encola 'GenerateBriefing'")
    Rel(beat_app, queue, "Push Task", "3. Encola tarea programada (8 AM)")
    
    Rel(worker_app, queue, "Pop Task", "4. Consume tareas")
    
    Rel(worker_app, db, "SQL (AsyncPG)", "5. Lee Prefs / Guarda Briefing")
    Rel(worker_app, rss, "HTTP GET", "6. Obtiene noticias crudas")
    Rel(worker_app, gemini, "HTTPS/API", "7. Solicita resumen IA")
    Rel(worker_app, smtp, "SMTP", "8. Envía email final")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

## Descripción del Diagrama

### Contenedores (Unidades Ejecutables)

| Contenedor | Tecnología | Descripción |
|-----------|-------------|-------------|
| NewsBrief API | Python, FastAPI, Uvicorn | Expone endpoints REST y valida requests |
| Celery Worker | Python, Celery | Ejecuta tareas pesadas: Fetch, IA, Notify |
| Celery Beat | Python, Celery | Scheduler que dispara tareas periódicas |
| PostgreSQL | PostgreSQL 16 | Persistencia de Dominio |
| Redis | Redis 7 | Message Broker para tareas Celery |

### Sistemas Externos

| Sistema | Descripción |
|---------|-------------|
| Google Gemini API | Generación de resúmenes con tono (LLM) |
| RSS Feeds | Fuentes de noticias externas |
| SMTP Server | Envío de notificaciones por email |

## Flujo de Datos

| Paso | De | A | Protocolo | Descripción |
|-----|---|---|----------|-------------|
| 1 | Usuario | NewsBrief API | HTTPS/REST | Configura preferencias |
| 2 | NewsBrief API | Redis | Push Task | Encola 'GenerateBriefing' |
| 3 | Celery Beat | Redis | Push Task | Encola tarea programada (8 AM) |
| 4 | Celery Worker | Redis | Pop Task | Consume tareas pendientes |
| 5 | Celery Worker | PostgreSQL | SQL (AsyncPG) | Lee prefs / Guarda briefing |
| 6 | Celery Worker | RSS Feeds | HTTP GET | Obtiene noticias crudas |
| 7 | Celery Worker | Google Gemini | HTTPS/API | Solicita resumen IA |
| 8 | Celery Worker | SMTP Server | SMTP | Envía email final |

## Correcciones vs Versión Anterior

| Aspecto | Versión Anterior | Versión Corregida |
|---------|-----------------|-------------------|
| DI como contenedor | Dependency Injection separado | Eliminado (es patrón de código) |
| Handlers | Contenedor separado | Eliminado (vive dentro de API) |
| Adapters | Contenedores separados | Eliminado (viven dentro de Worker) |
| Flujo Redis | Handler → Worker → Redis | API → Redis → Worker (correcto) |
| Beat | No existía | Agregado al diagrama |

## Notas Técnicas

- **Contenedores C4**: Representan unidades ejecutables independientes (no componentes de código)
- **Adapters**: Son clases Python que viven dentro del proceso del Worker, no son contenedores separados
- **Celery**: El Worker consume tareas desde Redis (message broker), no directamente de la API
- **Beat**: Scheduler que publica tareas periódicas a la cola de Redis