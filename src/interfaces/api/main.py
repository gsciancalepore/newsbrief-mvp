from fastapi import FastAPI
from src.interfaces.api.routes import preferences
from src.infrastructure.database.config import engine, Base

app = FastAPI(title="NewsBrief API")

# Incluir Routers
app.include_router(preferences.router)

# Evento de inicio para crear tablas (Solo para DEV/MVP, usar Alembic en PROD)
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
def health_check():
    return {"status": "ok"}