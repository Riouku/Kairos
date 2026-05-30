from app.schemas.asignacion import AsignacionCreate, AsignacionRead
from app.schemas.asignatura import AsignaturaCreate, AsignaturaRead, AsignaturaUpdate
from app.schemas.calendario import (
    CalendarioItem,
    CalendarioMesRead,
    CursoCreate,
    CursoRead,
    CursoUpdate,
    EventoAcademicoCreate,
    EventoAcademicoRead,
    EventoAcademicoUpdate,
    HorarioClaseCreate,
    HorarioClaseRead,
    HorarioClaseUpdate,
)
from app.schemas.dashboard import DashboardResumen, EstadisticaMensual
from app.schemas.profesor import ProfesorCreate, ProfesorRead, ProfesorUpdate

__all__ = [
    "AsignacionCreate",
    "AsignacionRead",
    "AsignaturaCreate",
    "AsignaturaRead",
    "AsignaturaUpdate",
    "CalendarioItem",
    "CalendarioMesRead",
    "CursoCreate",
    "CursoRead",
    "CursoUpdate",
    "DashboardResumen",
    "EstadisticaMensual",
    "EventoAcademicoCreate",
    "EventoAcademicoRead",
    "EventoAcademicoUpdate",
    "HorarioClaseCreate",
    "HorarioClaseRead",
    "HorarioClaseUpdate",
    "ProfesorCreate",
    "ProfesorRead",
    "ProfesorUpdate",
]
