# PipNews

Sistema de generación de briefings de noticias personalizados utilizando IA.

## Arquitectura

El proyecto sigue una arquitectura hexagonal (puertos y adaptadores) con separación clara de responsabilidades:

- **Dominio** (`src/domain/`): Lógica de negocio pura sin dependencias externas
- **Aplicación** (`src/application/`): Casos de uso y orquestación (CQRS)
- **Infraestructura** (`src/infrastructure/`): Implementaciones de bases de datos, APIs externas, etc.
- **Interfaces** (`src/interfaces/`): Puntos de entrada como API REST
- **Tests** (`tests/`): Suite de pruebas unitarias, de integración y e2e

## Tecnologías

- **Backend**: FastAPI, Python 3.9+
- **Base de datos**: PostgreSQL
- **Cache/Broker**: Redis
- **Tareas asíncronas**: Celery
- **Validación**: Pydantic
- **IA**: Soporte para múltiples proveedores (OpenAI GPT, Gemini Pro, etc.) mediante adapters
- **Testing**: Pytest

## Sistema de Notificaciones

El proyecto incluye un sistema de notificaciones que envía el resumen generado por email después de crear el briefing.

### Componentes
- `src/application/interfaces/notification_service.py`: Interfaz abstracta
- `src/infrastructure/external_api/email_adapter.py`: Implementación concreta
- Integración en `GenerateDailyBriefingHandler` con inyección de dependencias

### Flujo
1. Se genera el briefing con el resumen de noticias
2. Se persiste en la base de datos
3. Se envía el resumen por email al destinatario especificado en `GenerateDailyBriefingCommand.recipient_email`

## Cómo comenzar

### Prerrequisitos

- Docker y Docker Compose
- Clave de API para al menos un proveedor de IA (OpenAI o Gemini)

### Desarrollo local

1. Copiar variables de entorno:
   ```bash
   cp .env.example .env
   # Editar .env y añadir al menos una de:
   # OPENAI_API_KEY=tu_clave_openai
   # GEMINI_API_KEY=tu_clave_gemini
   ```

2. Iniciar los servicios:
   ```bash
   docker-compose up --build
   ```

3. La API estará disponible en: http://localhost:8000

### Desarrollo sin Docker

1. Crear entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Configurar variables de entorno en `.env`

4. Ejecutar la API:
   ```bash
   uvicorn src.interfaces.api.main:app --reload
   ```

## Comandos útiles

- Ejecutar todos los tests: `pytest -x`
- Ejecutar solo tests unitarios: `pytest tests/unit/ -x`
- Ver servicios Docker: `docker-compose ps`
- Ver logs: `docker-compose logs -f`

## Estructura de pruebas

### Configuración de Tests
- **Base de datos de test**: `newsbrief_test` (separada de producción)
- **Aislamiento**: Cada test tiene su propia sesión con rollback automático
- **Fixtures**: 
  - `setup_database`: Crea tablas con Base.metadata (scope="session")
  - `db_session`: Proporciona sesión con rollback por test (scope="function")
  - `event_loop`: Unifica el event loop para toda la suite (scope="session")

### Tipos de tests
- `tests/unit/`: Tests aislados de lógica de dominio
- `tests/integration/`: Tests que involucran múltiples capas (requieren BD)
- `tests/e2e/`: Tests de extremo a extremo de la API

## Convenciones de código

- La capa de dominio **no tiene** dependencias externas
- Se utiliza patrón CQRS: comandos en `/application/commands/`, consultas en `/application/queries/`
- Los DTOs se ubican en `/application/dto/` para definir los límites de los casos de uso
- Los adaptadores de infraestructura implementan las interfaces definidas en el dominio
- Los repositorios de dominio se definen en `src/domain/repositories/` y sus implementaciones en `src/infrastructure/database/repositories.py` (o similar)

## Notas Adicionales

- El caso de uso `create_preference` está en `src/application/commands/create_preference.py`
- El sistema soporta múltiples proveedores de IA (OpenAI y Gemini)
- Sistema de notificaciones integrado para enviar resúmenes por email
- GenerateDailyBriefingCommand ahora incluye `recipient_email` para notificaciones
- Los repositorios usan `flush()` en lugar de `commit()` para mejor aislamiento en tests