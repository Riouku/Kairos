import sys
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlsplit

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database import SessionLocal, get_db
from app.routes.auth import COOKIE_NAME, get_session, router as auth_router
from app.routes import (
    asignaciones_router,
    asignaturas_router,
    apoderados_router,
    asistencias_router,
    biblioteca_router,
    retiros_router,
    calendario_router,
    cursos_router,
    dashboard_router,
    estudiantes_router,
    evaluaciones_router,
    notas_router,
    periodos_router,
    profesores_router,
    reportes_router,
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
app.include_router(apoderados_router, prefix="/api")
app.include_router(asistencias_router, prefix="/api")
app.include_router(biblioteca_router, prefix="/api")
app.include_router(retiros_router, prefix="/api")
app.include_router(cursos_router, prefix="/api")
app.include_router(calendario_router, prefix="/api")
app.include_router(estudiantes_router, prefix="/api")
app.include_router(periodos_router, prefix="/api")
app.include_router(evaluaciones_router, prefix="/api")
app.include_router(notas_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(reportes_router, prefix="/api")
app.include_router(auth_router)


@app.middleware("http")
async def require_api_session(request: Request, call_next):
    path = request.url.path
    if request.method == "OPTIONS" or not path.startswith("/api/") or path in {
        "/api/auth/login", "/api/auth/solicitar-recuperacion", "/api/auth/restablecer-contrasena",
        "/api/health", "/api/health/db",
    }:
        return await call_next(request)
    # RPC authenticates the target path itself before forwarding the session cookie.
    if path == "/api/rpc":
        return await call_next(request)
    with SessionLocal() as db:
        session = get_session(db, request.cookies.get(COOKIE_NAME))
        if not session:
            return JSONResponse(status_code=401, content={"detail": "Inicia sesión para continuar."})
        if session.rol == "alumno" and path not in {
            "/api/portal/alumno", "/api/auth/me", "/api/auth/logout", "/api/auth/cambiar-contrasena",
        }:
            return JSONResponse(status_code=403, content={"detail": "Tu cuenta solo puede acceder a su portal de alumno."})
        if session.rol != "admin" and path in {"/api/auth/cuentas-alumno"}:
            return JSONResponse(status_code=403, content={"detail": "Acceso solo para administración."})
    return await call_next(request)


@app.post("/api/rpc", tags=["Sistema"])
async def api_rpc(payload: RpcRequest, request: Request, db=Depends(get_db)):
    if not payload.path.startswith("/api/") or payload.path.startswith("/api/rpc"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ruta RPC no permitida.")

    target_path = urlsplit(payload.path).path
    if target_path == "/api/auth/login":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El inicio de sesión debe usar su ruta directa.")
    session = get_session(db, request.cookies.get(COOKIE_NAME))
    if not session:
        raise HTTPException(status_code=401, detail="Inicia sesión para continuar.")
    if session.rol == "alumno" and target_path not in {
        "/api/portal/alumno", "/api/auth/me", "/api/auth/logout", "/api/auth/cambiar-contrasena",
    }:
        raise HTTPException(status_code=403, detail="Tu cuenta solo puede consultar su propio portal.")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://kairos.internal") as client:
        response = await client.request(payload.method, payload.path, json=payload.body,
                                       headers={"cookie": request.headers.get("cookie", "")})

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
