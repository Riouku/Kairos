from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class Asistencia(Base):
    __tablename__ = "asistencias"
    __table_args__ = (
        UniqueConstraint("estudiante_id", "fecha", name="uq_asistencia_estudiante_fecha"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    estudiante_id: Mapped[int] = mapped_column(ForeignKey("estudiantes.id"), nullable=False, index=True)
    curso_id: Mapped[int] = mapped_column(ForeignKey("cursos.id"), nullable=False, index=True)
    fecha: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="presente", index=True)
    observacion: Mapped[str | None] = mapped_column(Text, nullable=True)
    anio_academico: Mapped[int] = mapped_column(Integer, nullable=False, default=2026, index=True)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    estudiante = relationship("Estudiante", back_populates="asistencias")
    curso = relationship("Curso", back_populates="asistencias")
