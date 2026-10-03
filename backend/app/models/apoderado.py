from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class Apoderado(Base):
    __tablename__ = "apoderados"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    rut: Mapped[str | None] = mapped_column(String(12), nullable=True, unique=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    correo: Mapped[str | None] = mapped_column(String(150), nullable=True, index=True)
    telefono: Mapped[str | None] = mapped_column(String(30), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    vinculos = relationship("VinculoApoderado", back_populates="apoderado", cascade="all, delete-orphan")


class VinculoApoderado(Base):
    __tablename__ = "apoderados_estudiantes"

    id: Mapped[int] = mapped_column(primary_key=True)
    apoderado_id: Mapped[int] = mapped_column(ForeignKey("apoderados.id", ondelete="CASCADE"), nullable=False, index=True)
    estudiante_id: Mapped[int] = mapped_column(ForeignKey("estudiantes.id", ondelete="CASCADE"), nullable=False, index=True)
    parentesco: Mapped[str | None] = mapped_column(String(50), nullable=True)
    recibe_avisos: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    apoderado = relationship("Apoderado", back_populates="vinculos")
    estudiante = relationship("Estudiante")
