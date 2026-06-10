from datetime import date

from sqlalchemy import Boolean, Date, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class PeriodoAcademico(Base):
    __tablename__ = "periodos_academicos"
    __table_args__ = (
        UniqueConstraint("nombre", "anio_academico", name="uq_periodo_nombre_anio"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[date] = mapped_column(Date, nullable=False)
    anio_academico: Mapped[int] = mapped_column(Integer, nullable=False, default=2026, index=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    evaluaciones = relationship("Evaluacion", back_populates="periodo")
