from app.routes.asignaciones import router as asignaciones_router
from app.routes.asignaturas import router as asignaturas_router
from app.routes.asistencias import router as asistencias_router
from app.routes.calendario import router as calendario_router
from app.routes.cursos import router as cursos_router
from app.routes.dashboard import router as dashboard_router
from app.routes.estudiantes import router as estudiantes_router
from app.routes.evaluaciones import router as evaluaciones_router
from app.routes.notas import router as notas_router
from app.routes.periodos import router as periodos_router
from app.routes.profesores import router as profesores_router

__all__ = [
    "asignaciones_router",
    "asignaturas_router",
    "asistencias_router",
    "calendario_router",
    "cursos_router",
    "dashboard_router",
    "estudiantes_router",
    "evaluaciones_router",
    "notas_router",
    "periodos_router",
    "profesores_router",
]
