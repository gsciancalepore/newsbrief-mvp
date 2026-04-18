# 📰 NewsBrief MVP
> **SaaS de Curación de Noticias Automatizada con IA**
>
> Un sistema backend escalable y asíncrono que automatiza la búsqueda, resumen (con LLMs) y entrega personalizada de noticias. Diseñado bajo principios de **Clean Architecture**, **DDD** y **Event-Driven Design**.
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
---
## 🏗️ Arquitectura Técnica

El sistema sigue los principios de **Clean Architecture** y **Hexagonal Ports & Adapters**, separando estrictamente las reglas de negocio de los detalles de implementación.

¿Por qué tanta arquitectura para un MVP? Este proyecto no solo busca resolver el problema de negocio (resúmenes de noticias), sino demostrar capacidad de ingeniería de software a escala. La implementación de Clean Architecture, Hexagonal Ports & Adapters y CQRS está diseñada para:
- **Aislamiento de Dominio**: Permitir cambiar de proveedor de IA (Gemini a OpenAI) o fuente de noticias (RSS a API) sin refactorizar la lógica de negocio.
- **Escalabilidad Asíncrona**: Desacoplar la generación pesada de IA de la API REST para garantizar latencia <100ms en la interfaz de usuario.
- **Testabilidad**: Facilitar TDD estricto mediante inyección de dependencias, permitiendo mocks granulares en tests unitarios.

### Diagrama de Contexto (C4 Level 1)
```mermaid
C4Context
    title Sistema NewsBrief MVP - C4 Level 1 (Contexto)
    Person(usuario, "Usuario Final", "Suscriptor que configura preferencias y recibe resúmenes diarios.")
    System_Boundary(newsbrief, "NewsBrief System") {
        System(api, "NewsBrief API", "FastAPI", "Gestión de usuarios, preferencias y consulta de historial.")
        System(worker, "News Processor", "Celery Worker", "Orquestación: Búsqueda, Resumen IA y Notificación.")
        SystemDb(db, "PostgreSQL", "SQL Database", "Persistencia de entidades de dominio.")
        SystemQueue(queue, "Redis", "Message Broker", "Cola de tareas asíncronas.")
    }
    System_Ext(gemini, "Google Gemini API", "AI Service", "Generación de resúmenes con tono personalizado.")
    System_Ext(rss, "RSS Feeds", "External Data", "Fuentes de noticias crudas.")
    System_Ext(smtp, "SMTP Server", "Email Provider", "Envío de notificaciones.")
    Rel(usuario, api, "HTTPS/REST", "Configura temas y tonos")
    Rel(api, queue, "Push Task", "Encola 'GenerateBriefing'")
    Rel(worker, queue, "Pop Task", "Consume tareas pendientes")
    Rel(worker, db, "SQL (AsyncPG)", "Lee prefs / Guarda briefing")
    Rel(worker, rss, "HTTP GET", "Obtiene noticias crudas")
    Rel(worker, gemini, "HTTPS/API", "Solicita resumen estructurado")
    Rel(worker, smtp, "SMTP", "Envía resultado final")
```

### Stack Tecnológico

| Capa | Tecnología | Justificación |
|------|------------|---------------|
| Core | Python 3.11+ | Tipado fuerte y ecosistema maduro de IA. |
| Web Framework | FastAPI | Alto rendimiento asíncrono y validación automática con Pydantic. |
| Base de Datos | PostgreSQL 16 | Robustez relacional + soporte JSONB para flexibilidad. |
| ORM | SQLAlchemy Async | Acceso a datos no bloqueante (async/await). |
| Task Queue | Celery + Redis | Desacoplamiento de tareas pesadas (IA) y scheduling. |
| IA | Google Gemini 2.5 Flash-Lite | Balance costo/velocidad para resumen de textos. |
| Testing | Pytest + AsyncMock | TDD estricto y aislamiento de dependencias externas.

### Estructura del Proyecto

```
src/
├── domain/              # Reglas de negocio puras (Entidades, VOs, Interfaces)
├── application/        # Casos de uso (Commands, Handlers, Services)
├── infrastructure/     # Adaptadores concretos (DB, IA, Email, Celery)
└── interfaces/         # Entry points (FastAPI Routes, Schemas)
tests/
├── unit/               # Tests de dominio y aplicación (rápidos, sin I/O)
└── integration/        # Tests de infraestructura (con DB real/mockeada)
```

### ⚡ Características Clave
- Arquitectura Limpia: El dominio no conoce ni FastAPI ni SQLAlchemy.
- Asincronía Nativa: Uso de async/await en toda la cadena (API → DB → Workers).
- Patrón Strategy: Fuentes de noticias intercambiables (RSS, APIs externas).
- Patrón Adapter: Integración flexible con IA (Gemini) y Notificaciones (SMTP).
- TDD Completo: Cobertura de tests unitarios y de integración con mocks estratégicos.
- Idempotencia: Las tareas de Celery están diseñadas para ser seguras ante reintentos.
---

## 🐳 Ejecución con Docker (Recomendado)

Este proyecto está completamente orquestado con Docker Compose. No es necesario instalar Python ni dependencias localmente.

### Prerrequisitos
- Docker & Docker Compose instalados.
- Una API Key de Google Gemini.

### Pasos Rápidos

1. **Clonar y Configurar Entorno:**
   ```bash
   git clone https://github.com/gsciancalepore/newsbrief-mvp.git
   cd newsbrief-mvp
   cp .env.example .env
   ```
   Edita `.env` y agrega tu `GEMINI_API_KEY` real.

2. **Levantar el Sistema Completo:**
   ```bash
   docker compose up --build
   ```

3. **Verificar Estado:**
   - API Docs: http://localhost:8000/docs
   - Logs en tiempo real: `docker compose logs -f api`

4. **Detener y Limpiar:**
   ```bash
   docker compose down -v
   ```

### Nota Técnica
El healthcheck de PostgreSQL está configurado para especificar explícitamente la base de datos (`-d ${DB_NAME}`) para evitar conflictos de resolución de nombres por defecto en entornos Alpine.

Las migraciones de base de datos se ejecutan automáticamente al iniciar la API mediante Alembic. No es necesario ejecutar migraciones manualmente.

### 🔧 Desarrollo Avanzado (Sin Docker)
*Solo para contributors que necesiten debugging directo.*

Para desarrollo avanzado o debugging sin contenedores, consulta la guía de configuración manual en nuestra Documentación Interna.

---

### 🧪 Testing Strategy

El proyecto sigue una pirámide de tests estricta:

- **Unit Tests** (`tests/unit`): Validan Entidades, Value Objects y Handlers de aplicación usando AsyncMock. No tocan la DB ni la red.
- **Integration Tests** (`tests/integration`): Validan la interacción con PostgreSQL y la lógica completa de los casos de uso.

```bash
# Ejecutar solo tests unitarios (ultra rápidos)
pytest tests/unit -v

# Ejecutar suite completa
pytest -v
```
---
## 📄 Documentación Arquitectónica
Para profundizar en las decisiones de diseño, revisa los siguientes documentos:
- [C4 Level 1 - Contexto](docs/c4-level1.md): Interacción con sistemas externos.
- [C4 Level 2 - Contenedores](docs/c4-level2.md): Desglose de servicios internos (API, Worker, DB).
- [ARCHITECTURE.md](docs/ARCHITECTURE.md): Justificación técnica de patrones y stack.
---
👤 Autor
Gabriel Sciancalepore  
Software Architect & Backend Developer
- 🌐 [LinkedIn](https://linkedin.com/in/gabriel-sciancalepore-890328167)
- 💻 [GitHub](https://github.com/gsciancalepore)
---
💡 Nota para el Entrevistador
Este proyecto fue construitdo intencionalmente para demostrar dominio en arquitecturas empresariales modernas. Si tienes preguntas sobre por qué se eligió Clean Architecture sobre un monolito simple, o cómo se maneja la inyección de dependencias en un entorno asíncrono, ¡estaré encantado de discutirlas!