from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class Evaluacion(Base):
    __tablename__ = "evaluaciones"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    curso_id: Mapped[int] = mapped_column(ForeignKey("cursos.id"), nullable=False, index=True)
    asignatura_id: Mapped[int] = mapped_column(ForeignKey("asignaturas.id"), nullable=False, index=True)
    profesor_id: Mapped[int] = mapped_column(ForeignKey("profesores.id"), nullable=False, index=True)
    periodo_id: Mapped[int] = mapped_column(ForeignKey("periodos_academicos.id"), nullable=False, index=True)
    fecha: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    ponderacion: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    anio_academico: Mapped[int] = mapped_column(Integer, nullable=False, default=2026, index=True)
    estado: Mapped[str] = mapped_column(String(30), nullable=False, default="activa", index=True)

    curso = relationship("Curso", back_populates="evaluaciones")
    asignatura = relationship("Asignatura", back_populates="evaluaciones")
    profesor = relationship("Profesor", back_populates="evaluaciones")
    periodo = relationship("PeriodoAcademico", back_populates="evaluaciones")
    notas = relationship("Nota", back_populates="evaluacion")
