from sqlalchemy import Boolean, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class Curso(Base):
    __tablename__ = "cursos"
    __table_args__ = (
        UniqueConstraint("nombre", "jornada", "anio_academico", name="uq_curso_nombre_jornada_anio"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    nivel: Mapped[str] = mapped_column(String(80), nullable=False)
    letra: Mapped[str | None] = mapped_column(String(5), nullable=True)
    jornada: Mapped[str] = mapped_column(String(30), nullable=False)
    anio_academico: Mapped[int] = mapped_column(Integer, nullable=False, default=2026, index=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    eventos = relationship("EventoAcademico", back_populates="curso")
    horarios = relationship("HorarioClase", back_populates="curso", cascade="all, delete-orphan")
