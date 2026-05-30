from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class Asignatura(Base):
    __tablename__ = "asignaturas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    codigo: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    nivel: Mapped[str | None] = mapped_column(String(80), nullable=True)
    horas_semanales: Mapped[int | None] = mapped_column(Integer, nullable=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    asignaciones = relationship("Asignacion", back_populates="asignatura", cascade="all, delete-orphan")
    eventos_academicos = relationship("EventoAcademico", back_populates="asignatura")
    horarios_clases = relationship("HorarioClase", back_populates="asignatura")
