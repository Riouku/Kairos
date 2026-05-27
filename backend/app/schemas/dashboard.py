from app.schemas.asignacion import AsignacionRead
from pydantic import BaseModel


class EstadisticaMensual(BaseModel):
    mes: str
    total: int


class DashboardResumen(BaseModel):
    total_profesores: int
    total_asignaturas: int
    total_asignaciones: int
    asignaciones_mes_destacado: int
    mes_mas_activo: str
    estadisticas_mensuales: list[EstadisticaMensual]
    ultimas_asignaciones: list[AsignacionRead]
