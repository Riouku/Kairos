from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class Estudiante(Base):
    __tablename__ = "estudiantes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    rut: Mapped[str | None] = mapped_column(String(12), nullable=True, unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    correo: Mapped[str | None] = mapped_column(String(150), nullable=True, unique=True, index=True)
    curso_id: Mapped[int] = mapped_column(ForeignKey("cursos.id"), nullable=False, index=True)
    anio_academico: Mapped[int] = mapped_column(Integer, nullable=False, default=2026, index=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    curso = relationship("Curso", back_populates="estudiantes")
    notas = relationship("Nota", back_populates="estudiante")
    asistencias = relationship("Asistencia", back_populates="estudiante")
