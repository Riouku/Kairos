from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class Nota(Base):
    __tablename__ = "notas"
    __table_args__ = (
        UniqueConstraint("estudiante_id", "evaluacion_id", name="uq_nota_estudiante_evaluacion"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    estudiante_id: Mapped[int] = mapped_column(ForeignKey("estudiantes.id"), nullable=False, index=True)
    evaluacion_id: Mapped[int] = mapped_column(ForeignKey("evaluaciones.id"), nullable=False, index=True)
    nota: Mapped[Decimal] = mapped_column(Numeric(3, 1), nullable=False)
    observacion: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    estudiante = relationship("Estudiante", back_populates="notas")
    evaluacion = relationship("Evaluacion", back_populates="notas")
