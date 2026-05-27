from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import asignaciones_router, asignaturas_router, dashboard_router, profesores_router
from config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profesores_router, prefix="/api")
app.include_router(asignaturas_router, prefix="/api")
app.include_router(asignaciones_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")


@app.get("/health", tags=["Sistema"])
def health_check():
    return {"status": "ok", "app": settings.app_name}
