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

## Migraciones de Base de Datos

NewsBrief utiliza **Alembic** para gestionar el esquema de base de datos de forma versionada.

### Estrategia de Migraciones

| Aspecto | Implementación |
|---------|---------------|
| **Herramienta** | Alembic |
| **Ejecución** | Automática al iniciar API (Docker) |
| **Script** | entrypoint.sh con wait-for-db + alembic upgrade head |
| **Historial** | Versionado en alembic/versions/ |

### Flujo de Inicio

1. Docker Compose inicia el contenedor API
2. entrypoint.sh espera a que PostgreSQL esté disponible (wait-for-db)
3. Se ejecutan migraciones pendientes con `alembic upgrade head`
4. Una vez migrado, inicia Uvicorn

### Por qué Alembic?

| Beneficio | Descripción |
|----------|-------------|
| Versionado | Historial claro de cambios de esquema |
| Rollback | Posibilidad de revertir migraciones |
| Colaboración | Equipos pueden trabajar en paralelo |
| Producción | Gestionar esquemas sin perder datos |

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

## Trade-offs Arquitectónicos

| Decisión | Costo (Complejidad) | Beneficio (Valor Senior) |
|----------|---------------------|--------------------------|
| Clean Architecture | Más archivos, más interfaces, curva de aprendizaje inicial. | El dominio es puro Python. No depende de FastAPI ni SQLAlchemy. Fácil de migrar o extraer como librería. |
| Celery + Redis | Infraestructura adicional (broker), monitoreo más complejo. | Permite reintentos automáticos, scheduling (Beat) y manejo de picos de carga sin bloquear la API. |
| CQRS (Básico) | Separación de comandos y queries. | Claridad semántica. Los handlers de escritura no se mezclan con lógica de lectura. Preparado para escalado de lectura futuro. |
| DDD (Entidades/VOs) | Boilerplate inicial para Value Objects. | Validación temprana de datos. Imposible crear un estado inválido en el dominio (ej. email mal formado). |

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

---

## Resiliencia y Consistencia

NewsBrief implementa patrones de resiliencia para garantizar consistencia en operaciones asíncronas.

### Idempotencia

- Verificación de briefing existente en las últimas 24 horas antes de generar
- Evita costos duplicados de IA y spam de emails
- Implementado en `GenerateDailyBriefingHandler` via `get_latest_completed()`

### Retry Automático en Celery

- Tareas configuradas con `max_retries=3` y `default_retry_delay=60`
- Errores transitorios (DB, IA, SMTP) se reintentan automáticamente
- Decorador: `bind=True, autoretry_for=(Exception,), max_retries=3, default_retry_delay=60`

### Async Nativo Gemini
- Usa `client.aio` para llamadas no bloqueantes.
- Esto evita bloquear el event loop de asyncio durante las llamadas I/O a la API de Google, permitiendo una mayor concurrencia en el worker de Celery.
- Modelo: `gemini-2.5-flash-lite` (óptimo para velocidad).

### Persistencia (Unit of Work)
- Se adhiere al patrón Unit of Work: los repositorios solo realizan `flush()` para obtener IDs generados por la DB, mientras que el `commit()` final se gestiona en la capa de aplicación (Celery Task) para garantizar atomicidad y facilitar el testing con rollbacks.

| Environment | Comportamiento SMTP |
|-------------|-------------------|
| `production` | Credenciales obligatorias, lanza error si faltan |
| `development` | Simulación, loguea contenido sin enviar |

### Logging Detallado

Cada paso del flujo de generación de briefing es logueado:
- "Starting briefing generation for user {id}"
- "Fetching news for topics: [...]"
- "Summarizing {N} news items with tone '{tone}' via AI..."
- "Saving briefing to DB (status=COMPLETED)"
- "Sending email notification to {email}..."
- "Briefing completed for user {id}"

### Variables de Entorno

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `ENVIRONMENT` | Modo de ejecución | `development` |

## Concurrencia en Celery Workers

### Problema Original

Al ejecutar tareas de Celery con `concurrency > 1`, se producía el error:

```
InterfaceError: cannot perform operation: another operation is in progress
RuntimeError: Event loop is closed
```

Esto ocurría porque las conexiones asyncpg heredadas del proceso padre (prefork) estaban vinculadas al event loop del proceso padre, que ya no existe en los procesos hijos.

### Solución Implementada

| Componente | Configuración |
|------------|---------------|
| **SQLAlchemy** | `poolclass=NullPool` + `pool_pre_ping=True` |
| **Celery** | `--pool=prefork --concurrency=4` |

### Por qué NullPool?

Para Celery con pool prefork (procesos hijos), el pool de conexiones estándar compartiría conexiones entre procesos padre e hijos. Las conexiones heredadas tienen referencias a un event loop inexistente en el proceso hijo, causando el crash.

NullPool crea una conexión nueva por cada sesión, eliminando completamente este problema:
- **Aislamiento**: Cada proceso hijo tiene sus propias conexiones
- **Simplicidad**: No requiere gestión manual de ciclos de vida
- **Rendimiento**: El overhead es aceptable para workloads I/O-bound (IA, HTTP, DB)

### Configuración de Production

```yaml
# docker-compose.yml
command: celery -A src.infrastructure.celery.config.app worker --pool=prefork --concurrency=4 --loglevel=info
```

```python
# src/infrastructure/database/config.py
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    poolclass=NullPool,
    pool_pre_ping=True  # Verifica conexiones antes de usar
)
```

### Nota de Rendimiento

El uso de NullPool implica abrir y cerrar una conexión TCP por cada sesión de base de datos. En nuestro caso de uso (I/O bound con llamadas externas a IA y APIs), este overhead es insignificante comparado con el beneficio de estabilidad y aislamiento de procesos. Si en el futuro la carga de DB pura aumenta drásticamente, se podría evaluar volver a QueuePool implementando una fábrica de engines lazy-initializada por proceso.