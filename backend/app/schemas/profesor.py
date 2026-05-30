from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ProfesorBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    apellido: str = Field(..., min_length=1, max_length=100)
    rut: str | None = Field(default=None, max_length=12)
    correo: EmailStr = Field(..., max_length=150)
    telefono: str | None = Field(default=None, max_length=20)
    especialidad: str | None = Field(default=None, max_length=120)
    activo: bool = True


class ProfesorCreate(ProfesorBase):
    pass


class ProfesorUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    apellido: str | None = Field(default=None, min_length=1, max_length=100)
    rut: str | None = Field(default=None, max_length=12)
    correo: EmailStr | None = Field(default=None, max_length=150)
    telefono: str | None = Field(default=None, max_length=20)
    especialidad: str | None = Field(default=None, max_length=120)
    activo: bool | None = None


class ProfesorRead(ProfesorBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
