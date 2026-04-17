# PipNews - Guía para Agentes

## Comandos Esenciales
- Iniciar stack de desarrollo: `docker-compose up --build`
- Ejecutar tests: `pytest -x`
- Ejecutar solo tests unitarios: `pytest tests/unit/ -x`
- Ejecutar tests de integración: `pytest tests/integration/ -x`
- Iniciar API localmente: `uvicorn src.interfaces.api.main:app --reload`

## Estructura del Proyecto
- Dominio: `src/domain/` (lógica de negocio pura)
- Aplicación: `src/application/` (casos de uso/CQRS)
- Infraestructura: `src/infrastructure/` (BD, APIs externas, Celery)
- Interfaces: `src/interfaces/` (rutas API, esquemas)
- Tests: `tests/` (unit/integración/e2e)

## Dependencias Clave
- FastAPI (framework API)
- PostgreSQL (base de datos)
- Redis (broker/cache)
- Celery (tareas asíncronas)
- Pydantic (validación)
- OpenAI/Gemini (servicio de IA)

## Flujo de Verificación
1. Verificar que servicios Docker estén saludables: `docker-compose ps`
2. Ejecutar tests de dominio primero (rápidos, sin BD)
3. Ejecutar tests de integración (requiere BD/Redis)
4. Ejecutar tests de endpoints API al final

## Entorno
- Copiar `.env.example` a `.env` para desarrollo local
- Requerido: OPENAI_API_KEY o GEMINI_API_KEY
- Base de datos desarrollo: postgresql://newsbrief_user:secret_password@localhost:5432/newsbrief_db
- Base de datos test: postgresql://newsbrief_user:secret_password@localhost:5432/newsbrief_test
- Redis: redis://localhost:6379/0

## Testing

### Configuración de Tests
- Los tests de integración usan una base de datos separada: `newsbrief_test`
- Aislamiento mediante rollback por transacción (db_session fixture)
- Engine específico para tests con NullPool para evitar conflictos de event loop
- Fixture `event_loop` con scope="session" para unificar event loop

### Comandos de Tests
- Todos los tests: `pytest -x`
- Tests unitarios: `pytest tests/unit/ -x`
- Tests integración: `pytest tests/integration/ -x`
- Tests e2e: `pytest tests/e2e/ -x`

## Convenciones de Código
- Capa de dominio tiene cero dependencias externas
- Usar CQRS: Comandos (escrituras) en `/commands`, Consultas (lecturas) en `/queries`
- DTOs en `/application/dto` para límites de casos de uso
- Adaptadores de infraestructura implementan interfaces de dominio
- Los repositorios de dominio se definen en `src/domain/repositories/` y sus implementaciones en `src/infrastructure/database/repositories.py` (o similar)
- Los interfaces específicos de la capa de aplicación (como servicios de IA y notificaciones) se encuentran en `src/application/interfaces/`

## Notas Adicionales
- El caso de uso `create_preference` está en `src/application/commands/create_preference.py`
- Sistema de notificaciones integrado: `EmailNotificationAdapter` envía resumen por email
- GenerateDailyBriefingHandler recibe `notification_service` como dependencia
- Los repositorios usan `flush()` en lugar de `commit()` para mejor aislamiento en tests
- El archivo `src/application/interfaces/repositories.py` existe pero está vacío; las interfaces de repositorio correctamente residen en `src/domain/repositories/`