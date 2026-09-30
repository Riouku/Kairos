from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base

class RetiroEstudiante(Base):
    __tablename__ = "retiros_estudiantes"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    estudiante_id: Mapped[int] = mapped_column(ForeignKey("estudiantes.id"), nullable=False, index=True)
    retirado_por: Mapped[str] = mapped_column(String(150), nullable=False)
    autorizado_por: Mapped[str] = mapped_column(String(150), nullable=False)
    motivo: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha_hora: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), index=True)
    estudiante = relationship("Estudiante")
