from app.schemas.asignacion import AsignacionRead
from app.schemas.notas import NotaRead
from pydantic import BaseModel


class EstadisticaMensual(BaseModel):
    mes: str
    total: int


class DashboardResumen(BaseModel):
    total_profesores: int
    total_asignaturas: int
    total_asignaciones: int
    total_estudiantes: int = 0
    total_evaluaciones: int = 0
    total_notas: int = 0
    total_asistencias: int = 0
    promedio_general: float | None = None
    porcentaje_asistencia: float | None = None
    asignaciones_mes_destacado: int
    mes_mas_activo: str
    estadisticas_mensuales: list[EstadisticaMensual]
    ultimas_asignaciones: list[AsignacionRead]
    ultimas_notas: list[NotaRead] = []
