import sys
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database import SessionLocal
from app.routes import (
    asignaciones_router,
    asignaturas_router,
    asistencias_router,
    calendario_router,
    cursos_router,
    dashboard_router,
    estudiantes_router,
    evaluaciones_router,
    notas_router,
    periodos_router,
    profesores_router,
)
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
app.include_router(asistencias_router, prefix="/api")
app.include_router(cursos_router, prefix="/api")
app.include_router(calendario_router, prefix="/api")
app.include_router(estudiantes_router, prefix="/api")
app.include_router(periodos_router, prefix="/api")
app.include_router(evaluaciones_router, prefix="/api")
app.include_router(notas_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")


@app.exception_handler(SQLAlchemyError)
def sqlalchemy_exception_handler(_request: Request, _exc: SQLAlchemyError):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": (
                "No se pudo consultar PostgreSQL. Verifica que el servicio este iniciado "
                "y que DATABASE_URL apunte a una base de datos disponible."
            )
        },
    )


@app.get("/health", tags=["Sistema"])
def health_check():
    return {"status": "ok", "app": settings.app_name}


@app.get("/health/db", tags=["Sistema"])
def database_health_check():
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}
