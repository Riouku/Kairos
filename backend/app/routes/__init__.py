from app.routes.asignaciones import router as asignaciones_router
from app.routes.asignaturas import router as asignaturas_router
from app.routes.asistencias import router as asistencias_router
from app.routes.apoderados import router as apoderados_router
from app.routes.biblioteca import router as biblioteca_router
from app.routes.retiros import router as retiros_router
from app.routes.calendario import router as calendario_router
from app.routes.cursos import router as cursos_router
from app.routes.dashboard import router as dashboard_router
from app.routes.estudiantes import router as estudiantes_router
from app.routes.evaluaciones import router as evaluaciones_router
from app.routes.notas import router as notas_router
from app.routes.periodos import router as periodos_router
from app.routes.profesores import router as profesores_router
from app.routes.reportes import router as reportes_router

__all__ = [
    "asignaciones_router",
    "asignaturas_router",
    "asistencias_router",
    "apoderados_router",
    "biblioteca_router",
    "retiros_router",
    "calendario_router",
    "cursos_router",
    "dashboard_router",
    "estudiantes_router",
    "evaluaciones_router",
    "notas_router",
    "periodos_router",
    "profesores_router",
    "reportes_router",
]
