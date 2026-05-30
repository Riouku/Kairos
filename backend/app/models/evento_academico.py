from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class EventoAcademico(Base):
    __tablename__ = "eventos_academicos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha_inicio: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    fecha_fin: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    curso_id: Mapped[int | None] = mapped_column(ForeignKey("cursos.id", ondelete="SET NULL"), nullable=True, index=True)
    profesor_id: Mapped[int | None] = mapped_column(ForeignKey("profesores.id", ondelete="SET NULL"), nullable=True, index=True)
    asignatura_id: Mapped[int | None] = mapped_column(ForeignKey("asignaturas.id", ondelete="SET NULL"), nullable=True, index=True)
    anio_academico: Mapped[int] = mapped_column(Integer, nullable=False, default=2026, index=True)
    estado: Mapped[str] = mapped_column(String(30), nullable=False, default="activo", index=True)

    curso = relationship("Curso", back_populates="eventos")
    profesor = relationship("Profesor", back_populates="eventos_academicos")
    asignatura = relationship("Asignatura", back_populates="eventos_academicos")
