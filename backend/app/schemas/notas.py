from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


EvaluacionEstado = Literal["activa", "cerrada", "cancelada"]


class EstudianteBase(BaseModel):
    rut: str | None = Field(default=None, max_length=12)
    nombre: str = Field(..., min_length=1, max_length=100)
    apellido: str = Field(..., min_length=1, max_length=100)
    correo: EmailStr | None = Field(default=None, max_length=150)
    curso_id: int
    anio_academico: int = Field(default=2026, ge=2000, le=2100)
    activo: bool = True


class EstudianteCreate(EstudianteBase):
    pass


class EstudianteUpdate(BaseModel):
    rut: str | None = Field(default=None, max_length=12)
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    apellido: str | None = Field(default=None, min_length=1, max_length=100)
    correo: EmailStr | None = Field(default=None, max_length=150)
    curso_id: int | None = None
    anio_academico: int | None = Field(default=None, ge=2000, le=2100)
    activo: bool | None = None


class EstudianteRead(EstudianteBase):
    id: int
    curso_nombre: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PeriodoAcademicoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    fecha_inicio: date
    fecha_fin: date
    anio_academico: int = Field(default=2026, ge=2000, le=2100)
    activo: bool = True

    @model_validator(mode="after")
    def validate_fechas(self):
        if self.fecha_fin < self.fecha_inicio:
            raise ValueError("La fecha fin debe ser mayor o igual que la fecha inicio.")
        return self


class PeriodoAcademicoCreate(PeriodoAcademicoBase):
    pass


class PeriodoAcademicoUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    anio_academico: int | None = Field(default=None, ge=2000, le=2100)
    activo: bool | None = None


class PeriodoAcademicoRead(PeriodoAcademicoBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class EvaluacionBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=150)
    descripcion: str | None = None
    curso_id: int
    asignatura_id: int
    profesor_id: int
    periodo_id: int
    fecha: date
    ponderacion: float = Field(..., ge=0, le=100)
    anio_academico: int = Field(default=2026, ge=2000, le=2100)
    estado: EvaluacionEstado = "activa"


class EvaluacionCreate(EvaluacionBase):
    pass


class EvaluacionUpdate(BaseModel):
    titulo: str | None = Field(default=None, min_length=1, max_length=150)
    descripcion: str | None = None
    curso_id: int | None = None
    asignatura_id: int | None = None
    profesor_id: int | None = None
    periodo_id: int | None = None
    fecha: date | None = None
    ponderacion: float | None = Field(default=None, ge=0, le=100)
    anio_academico: int | None = Field(default=None, ge=2000, le=2100)
    estado: EvaluacionEstado | None = None


class EvaluacionRead(EvaluacionBase):
    id: int
    curso_nombre: str | None = None
    asignatura_nombre: str | None = None
    profesor_nombre: str | None = None
    periodo_nombre: str | None = None
    notas_registradas: int = 0

    model_config = ConfigDict(from_attributes=True)


class NotaBase(BaseModel):
    estudiante_id: int
    evaluacion_id: int
    nota: float = Field(..., ge=1.0, le=7.0)
    observacion: str | None = None

    @field_validator("nota")
    @classmethod
    def validate_un_decimal(cls, value: float) -> float:
        if round(value * 10, 6) != round(value * 10):
            raise ValueError("La nota debe tener maximo un decimal.")
        return round(value, 1)


class NotaCreate(NotaBase):
    pass


class NotaUpdate(BaseModel):
    nota: float | None = Field(default=None, ge=1.0, le=7.0)
    observacion: str | None = None

    @field_validator("nota")
    @classmethod
    def validate_un_decimal(cls, value: float | None) -> float | None:
        if value is None:
            return value
        if round(value * 10, 6) != round(value * 10):
            raise ValueError("La nota debe tener maximo un decimal.")
        return round(value, 1)


class NotaRead(NotaBase):
    id: int
    fecha_registro: datetime
    estudiante_nombre: str | None = None
    evaluacion_titulo: str | None = None
    curso_nombre: str | None = None
    asignatura_nombre: str | None = None
    profesor_nombre: str | None = None
    periodo_nombre: str | None = None
    ponderacion: float | None = None

    model_config = ConfigDict(from_attributes=True)


class NotaResumenItem(BaseModel):
    estudiante_id: int
    estudiante_nombre: str
    curso_id: int
    curso_nombre: str
    asignatura_id: int
    asignatura_nombre: str
    periodo_id: int
    periodo_nombre: str
    anio_academico: int
    promedio: float | None
    notas_registradas: int
    ponderacion_registrada: float


class NotaResumenRead(BaseModel):
    promedio_general: float | None
    items: list[NotaResumenItem]
