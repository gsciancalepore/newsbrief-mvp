# Arquitectura NewsBrief MVP

## Visión General
NewsBrief es un sistema SaaS asíncrono diseñado para la curación automatizada de noticias. Utiliza una arquitectura orientada a eventos para desacoplar la interacción del usuario (baja latencia) del procesamiento pesado de IA (alta latencia).

## Stack Tecnológico

| Tecnología | Uso Estratégico |
|-------------|-----|
| **Python 3.11+** | Lenguaje principal por su ecosistema de IA y tipado fuerte. |
| **FastAPI** | Framework web asíncrono para alta concurrencia en I/O. |
| **SQLAlchemy Async** | ORM para acceso a datos no bloqueante con PostgreSQL. |
| **Celery + Redis** | Orquestación de tareas en segundo plano y scheduling. |
| **PostgreSQL 16** | Base de datos relacional robusta con soporte JSONB. |
| **Google Gemini** | LLM para resumen y adaptación de tono de noticias. |

## Patrones Arquitectónicos

### 1. Clean Architecture & Hexagonal
El núcleo del negocio es independiente de frameworks y bases de datos.
- **Dominio (`src/domain`)**: Entidades puras y reglas de negocio. Sin dependencias externas.
- **Aplicación (`src/application`)**: Casos de uso que orquestan el flujo.
- **Infraestructura (`src/infrastructure`)**: Adaptadores concretos (DB, IA, Email).
- **Interfaces (`src/interfaces`)**: Entry points (API REST, CLI).

### 2. Domain-Driven Design (DDD)
Modelado basado en el lenguaje ubicuo del negocio:
- **Aggregate Roots**: `User`, `Briefing`.
- **Value Objects**: `Email`, `Topic`, `Tone` (inmutables y auto-validados).

### 3. CQRS (Command Query Responsibility Segregation)
Separación clara entre escritura y lectura:
- **Commands**: `CreatePreferenceCommand`, `GenerateDailyBriefingCommand`.
- **Queries**: `GetUserBriefingsQuery` (optimizadas para lectura).

### 4. Strategy & Adapter Patterns
- **Strategy**: `NewsFetcherService` permite intercambiar fuentes (RSS, NewsAPI) sin cambiar la lógica de negocio.
- **Adapter**: `GeminiSummarizerAdapter` y `EmailNotificationAdapter` encapsulan servicios externos.

## Flujo de Datos Crítico

1. **Configuración**: Usuario → FastAPI (HTTPS) → DB (Persistencia inmediata).
2. **Trigger**: Celery Beat → Redis (Encola tarea programada a las 8 AM).
3. **Procesamiento**:
   - Celery Worker → Redis (Consume tarea).
   - Worker → DB (Obtiene preferencias del usuario).
   - Worker → RSS Feeds (Obtiene noticias crudas).
   - Worker → Gemini API (Genera resumen con tono personalizado).
   - Worker → DB (Guarda el Briefing generado).
   - Worker → SMTP (Envía notificación al usuario).

## Decisiones Arquitectónicas Clave

### 1. Asincronía (Async/Await)
- **Decisión**: Uso de `asyncpg` y FastAPI asíncrono.
- **Justificación**: Permite manejar alta concurrencia en la API con mínimos recursos, ya que la mayoría de las operaciones son I/O bound (esperar a la DB o a Redis).

### 2. Offloading a Celery
- **Decisión**: Mover la generación de briefings a workers en segundo plano.
- **Justificación**: Las llamadas a LLMs (IA) son lentas y costosas. Bloquear la API HTTP sería inaceptable para la UX. Celery permite reintentos automáticos y escalabilidad horizontal del procesamiento.

### 3. Inversión de Dependencias (DIP)
- **Decisión**: Los casos de uso dependen de interfaces (`Repository`, `AIService`), no de implementaciones.
- **Justificación**: Facilita el testing unitario mediante mocks y permite cambiar proveedores (ej. de Gemini a OpenAI) sin tocar la lógica de negocio.

### 4. Resiliencia
- **Decisión**: Uso de colas persistentes en Redis y reintentos en Celery.
- **Justificación**: Si un servicio externo (RSS o Gemini) falla temporalmente, la tarea no se pierde; se reintenta automáticamente según la política configurada.

## Sistema de Notificaciones

NewsBrief utiliza un adapter de notificaciones para enviar los briefings generados por email:

### Componentes

| Componente | Responsabilidad |
|------------|------------------|
| `NotificationService` (Interfaz) | Define el contrato `send_summary(recipient, summary_text)` |
| `EmailNotificationAdapter` | Implementación concreta que usa SMTP para enviar emails |

### Flujo de Notificación

1. El `GenerateDailyBriefingHandler` completa la generación del briefing
2. Llama al `notification_service.send_summary()` con el email del usuario y el contenido
3. El adapter verifica credenciales SMTP (variables de entorno)
4. Si están configuradas, envía el email; si no, simula el envío (modo desarrollo)

### Configuración de Variables de Entorno

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `SMTP_SERVER` | Servidor SMTP | `smtp.gmail.com` |
| `SMTP_PORT` | Puerto SMTP | `587` |
| `SENDER_EMAIL` | Email remitente | `newsbrief@gmail.com` |
| `SENDER_PASSWORD` | App Password de Gmail | `xxxx xxxx xxxx xxxx` |
| `DEFAULT_RECIPIENT_EMAIL` | Email por defecto para tareas Celery | `user@example.com` |

### Patrón Adapter

El sistema de notificaciones sigue el patrón Adapter para permitir intercambio de implementaciones:
- Para **desarrollo local**: Simulación sin enviar emails reales
- Para **producción**: Configuración SMTP real
- Para **futuro**: Integración con SendGrid, AWS SES, etc.