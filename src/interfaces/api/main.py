from fastapi import FastAPI
from src.interfaces.api.routes import preferences

app = FastAPI(title="NewsBrief API")

# Incluir Routers
app.include_router(preferences.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}