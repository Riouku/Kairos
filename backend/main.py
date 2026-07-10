import sys
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlsplit

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel, Field
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


class RpcRequest(BaseModel):
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
    path: str = Field(..., min_length=1)
    body: dict[str, Any] | None = None

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


@app.post("/api/rpc", tags=["Sistema"])
async def api_rpc(payload: RpcRequest):
    if not payload.path.startswith("/api/") or payload.path.startswith("/api/rpc"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ruta RPC no permitida.")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://kairos.internal") as client:
        response = await client.request(payload.method, payload.path, json=payload.body)

    if response.status_code == status.HTTP_204_NO_CONTENT:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type:
        return JSONResponse(status_code=response.status_code, content=response.json())
    return Response(status_code=response.status_code, content=response.content, media_type=content_type or None)


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


@app.get("/api/health", tags=["Sistema"])
def api_health_check():
    return health_check()


@app.get("/health/db", tags=["Sistema"])
def database_health_check():
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PostgreSQL no esta disponible. Revisa DATABASE_URL y que las migraciones esten aplicadas.",
        ) from exc
    return {"status": "ok", "database": "connected"}


@app.get("/api/health/db", tags=["Sistema"])
def api_database_health_check():
    return database_health_check()


@app.get("/api/diagnostico/db", tags=["Sistema"])
def database_diagnostics():
    parsed_url = urlsplit(settings.database_url)
    diagnostic = {
        "database_url_configurada": bool(settings.database_url),
        "driver": parsed_url.scheme,
        "host": parsed_url.hostname,
        "puerto": parsed_url.port,
        "base": parsed_url.path.lstrip("/") or None,
    }
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except Exception as exc:
        diagnostic.update(
            {
                "conexion": "error",
                "error_tipo": exc.__class__.__name__,
                "error": str(exc).splitlines()[0][:300],
            }
        )
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=diagnostic)
    diagnostic["conexion"] = "ok"
    return diagnostic
