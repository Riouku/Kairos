from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


AsistenciaEstado = Literal["presente", "ausente", "tarde", "justificado"]


class AsistenciaBase(BaseModel):
    estudiante_id: int
    curso_id: int
    fecha: date
    estado: AsistenciaEstado = "presente"
    observacion: str | None = None
    anio_academico: int = Field(default=2026, ge=2000, le=2100)


class AsistenciaCreate(AsistenciaBase):
    pass


class AsistenciaUpdate(BaseModel):
    estado: AsistenciaEstado | None = None
    observacion: str | None = None


class AsistenciaBulkItem(BaseModel):
    estudiante_id: int
    estado: AsistenciaEstado = "presente"
    observacion: str | None = None


class AsistenciaBulkCreate(BaseModel):
    curso_id: int
    fecha: date
    anio_academico: int = Field(default=2026, ge=2000, le=2100)
    registros: list[AsistenciaBulkItem]


class AsistenciaRead(AsistenciaBase):
    id: int
    fecha_registro: datetime
    estudiante_nombre: str | None = None
    curso_nombre: str | None = None

    model_config = ConfigDict(from_attributes=True)


class AsistenciaResumenRead(BaseModel):
    curso_id: int | None = None
    mes: int
    anio_academico: int
    total_registros: int
    presentes: int
    ausentes: int
    tardes: int
    justificados: int
    porcentaje_asistencia: float | None
