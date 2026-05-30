from datetime import datetime, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


EventoTipo = Literal["evaluacion", "reunion", "feriado", "actividad", "periodo", "clase"]
EventoEstado = Literal["activo", "cancelado", "finalizado"]


class CursoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    nivel: str = Field(..., min_length=1, max_length=80)
    letra: str | None = Field(default=None, max_length=5)
    jornada: str = Field(..., min_length=1, max_length=30)
    anio_academico: int = Field(default=2026, ge=2000, le=2100)
    activo: bool = True


class CursoCreate(CursoBase):
    pass


class CursoUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    nivel: str | None = Field(default=None, min_length=1, max_length=80)
    letra: str | None = Field(default=None, max_length=5)
    jornada: str | None = Field(default=None, min_length=1, max_length=30)
    anio_academico: int | None = Field(default=None, ge=2000, le=2100)
    activo: bool | None = None


class CursoRead(CursoBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class EventoAcademicoBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=150)
    descripcion: str | None = None
    fecha_inicio: datetime
    fecha_fin: datetime | None = None
    tipo: EventoTipo
    curso_id: int | None = None
    profesor_id: int | None = None
    asignatura_id: int | None = None
    anio_academico: int = Field(default=2026, ge=2000, le=2100)
    estado: EventoEstado = "activo"

    @model_validator(mode="after")
    def validate_fecha_fin(self):
        if self.fecha_fin and self.fecha_fin <= self.fecha_inicio:
            raise ValueError("La fecha fin debe ser mayor que la fecha inicio.")
        return self


class EventoAcademicoCreate(EventoAcademicoBase):
    pass


class EventoAcademicoUpdate(BaseModel):
    titulo: str | None = Field(default=None, min_length=1, max_length=150)
    descripcion: str | None = None
    fecha_inicio: datetime | None = None
    fecha_fin: datetime | None = None
    tipo: EventoTipo | None = None
    curso_id: int | None = None
    profesor_id: int | None = None
    asignatura_id: int | None = None
    anio_academico: int | None = Field(default=None, ge=2000, le=2100)
    estado: EventoEstado | None = None


class EventoAcademicoRead(EventoAcademicoBase):
    id: int
    curso_nombre: str | None = None
    profesor_nombre: str | None = None
    asignatura_nombre: str | None = None

    model_config = ConfigDict(from_attributes=True)


class HorarioClaseBase(BaseModel):
    curso_id: int
    profesor_id: int
    asignatura_id: int
    dia_semana: int = Field(..., ge=1, le=7)
    hora_inicio: time
    hora_fin: time
    anio_academico: int = Field(default=2026, ge=2000, le=2100)
    activo: bool = True

    @model_validator(mode="after")
    def validate_horas(self):
        if self.hora_fin <= self.hora_inicio:
            raise ValueError("La hora fin debe ser mayor que la hora inicio.")
        return self


class HorarioClaseCreate(HorarioClaseBase):
    pass


class HorarioClaseUpdate(BaseModel):
    curso_id: int | None = None
    profesor_id: int | None = None
    asignatura_id: int | None = None
    dia_semana: int | None = Field(default=None, ge=1, le=7)
    hora_inicio: time | None = None
    hora_fin: time | None = None
    anio_academico: int | None = Field(default=None, ge=2000, le=2100)
    activo: bool | None = None


class HorarioClaseRead(HorarioClaseBase):
    id: int
    curso_nombre: str
    profesor_nombre: str
    asignatura_nombre: str
    asignatura_codigo: str

    model_config = ConfigDict(from_attributes=True)


class CalendarioItem(BaseModel):
    id: str
    source: Literal["evento", "horario"]
    source_id: int
    titulo: str
    tipo: EventoTipo
    fecha_inicio: datetime
    fecha_fin: datetime | None = None
    curso_id: int | None = None
    curso_nombre: str | None = None
    profesor_id: int | None = None
    profesor_nombre: str | None = None
    asignatura_id: int | None = None
    asignatura_nombre: str | None = None
    asignatura_codigo: str | None = None
    estado: str = "activo"


class CalendarioMesRead(BaseModel):
    anio: int
    mes: int
    items: list[CalendarioItem]
