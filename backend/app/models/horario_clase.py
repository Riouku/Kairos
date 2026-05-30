from datetime import time

from sqlalchemy import Boolean, ForeignKey, Integer, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class HorarioClase(Base):
    __tablename__ = "horarios_clases"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    curso_id: Mapped[int] = mapped_column(ForeignKey("cursos.id"), nullable=False, index=True)
    profesor_id: Mapped[int] = mapped_column(ForeignKey("profesores.id"), nullable=False, index=True)
    asignatura_id: Mapped[int] = mapped_column(ForeignKey("asignaturas.id"), nullable=False, index=True)
    dia_semana: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    hora_inicio: Mapped[time] = mapped_column(Time, nullable=False)
    hora_fin: Mapped[time] = mapped_column(Time, nullable=False)
    anio_academico: Mapped[int] = mapped_column(Integer, nullable=False, default=2026, index=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    curso = relationship("Curso", back_populates="horarios")
    profesor = relationship("Profesor", back_populates="horarios_clases")
    asignatura = relationship("Asignatura", back_populates="horarios_clases")
