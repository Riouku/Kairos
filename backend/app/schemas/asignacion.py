from datetime import date

from pydantic import BaseModel, ConfigDict


class AsignacionCreate(BaseModel):
    profesor_id: int
    asignatura_id: int
    fecha_asignacion: date | None = None


class AsignacionRead(BaseModel):
    id: int
    profesor_id: int
    asignatura_id: int
    fecha_asignacion: date
    profesor_nombre: str
    asignatura_nombre: str
    asignatura_codigo: str

    model_config = ConfigDict(from_attributes=True)
