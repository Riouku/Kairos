from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class Profesor(Base):
    __tablename__ = "profesores"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    correo: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    telefono: Mapped[str | None] = mapped_column(String(20), nullable=True)

    asignaciones = relationship("Asignacion", back_populates="profesor", cascade="all, delete-orphan")
