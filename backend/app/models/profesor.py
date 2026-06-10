from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class Profesor(Base):
    __tablename__ = "profesores"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    rut: Mapped[str | None] = mapped_column(String(12), nullable=True, unique=True, index=True)
    correo: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    telefono: Mapped[str | None] = mapped_column(String(20), nullable=True)
    especialidad: Mapped[str | None] = mapped_column(String(120), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    asignaciones = relationship("Asignacion", back_populates="profesor", cascade="all, delete-orphan")
    eventos_academicos = relationship("EventoAcademico", back_populates="profesor")
    horarios_clases = relationship("HorarioClase", back_populates="profesor")
    evaluaciones = relationship("Evaluacion", back_populates="profesor")
