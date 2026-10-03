from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class CuentaEstudiante(Base):
    __tablename__ = "cuentas_estudiante"

    id: Mapped[int] = mapped_column(primary_key=True)
    estudiante_id: Mapped[int] = mapped_column(ForeignKey("estudiantes.id", ondelete="CASCADE"), unique=True, index=True)
    correo: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    estudiante = relationship("Estudiante")


class SesionUsuario(Base):
    __tablename__ = "sesiones_usuario"

    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    rol: Mapped[str] = mapped_column(String(20), nullable=False)
    cuenta_estudiante_id: Mapped[int | None] = mapped_column(ForeignKey("cuentas_estudiante.id", ondelete="CASCADE"), nullable=True, index=True)
    expira_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    creada_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class TokenRecuperacion(Base):
    __tablename__ = "tokens_recuperacion"

    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    cuenta_estudiante_id: Mapped[int] = mapped_column(ForeignKey("cuentas_estudiante.id", ondelete="CASCADE"), nullable=False, index=True)
    expira_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    cuenta = relationship("CuentaEstudiante")
