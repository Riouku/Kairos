from app.routes.asignaciones import router as asignaciones_router
from app.routes.asignaturas import router as asignaturas_router
from app.routes.dashboard import router as dashboard_router
from app.routes.profesores import router as profesores_router

__all__ = [
    "asignaciones_router",
    "asignaturas_router",
    "dashboard_router",
    "profesores_router",
]
