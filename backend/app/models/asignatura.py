from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class Asignatura(Base):
    __tablename__ = "asignaturas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    codigo: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)

    asignaciones = relationship("Asignacion", back_populates="asignatura", cascade="all, delete-orphan")
