from pydantic import BaseModel, ConfigDict, Field


class AsignaturaBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    codigo: str = Field(..., min_length=1, max_length=20)
    nivel: str | None = Field(default=None, max_length=80)
    horas_semanales: int | None = Field(default=None, ge=1, le=60)
    descripcion: str | None = None
    activo: bool = True


class AsignaturaCreate(AsignaturaBase):
    pass


class AsignaturaUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    codigo: str | None = Field(default=None, min_length=1, max_length=20)
    nivel: str | None = Field(default=None, max_length=80)
    horas_semanales: int | None = Field(default=None, ge=1, le=60)
    descripcion: str | None = None
    activo: bool | None = None


class AsignaturaRead(AsignaturaBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
