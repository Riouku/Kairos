from datetime import date

from sqlalchemy import Date, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class Asignacion(Base):
    __tablename__ = "asignaciones"
    __table_args__ = (
        UniqueConstraint("profesor_id", "asignatura_id", name="uq_profesor_asignatura"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    profesor_id: Mapped[int] = mapped_column(ForeignKey("profesores.id"), nullable=False, index=True)
    asignatura_id: Mapped[int] = mapped_column(ForeignKey("asignaturas.id"), nullable=False, index=True)
    fecha_asignacion: Mapped[date] = mapped_column(Date, nullable=False, server_default=func.current_date())

    profesor = relationship("Profesor", back_populates="asignaciones")
    asignatura = relationship("Asignatura", back_populates="asignaciones")
