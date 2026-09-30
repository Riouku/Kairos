from datetime import date, datetime
from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base

class Libro(Base):
    __tablename__ = "libros"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    autor: Mapped[str] = mapped_column(String(150), nullable=False)
    isbn: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    ejemplares: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    prestamos = relationship("PrestamoLibro", back_populates="libro")

class PrestamoLibro(Base):
    __tablename__ = "prestamos_libros"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    libro_id: Mapped[int] = mapped_column(ForeignKey("libros.id"), nullable=False, index=True)
    estudiante_id: Mapped[int] = mapped_column(ForeignKey("estudiantes.id"), nullable=False, index=True)
    fecha_prestamo: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    fecha_devolucion: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    devuelto_en: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    libro = relationship("Libro", back_populates="prestamos")
    estudiante = relationship("Estudiante")


class PedidoLibro(Base):
    __tablename__ = "pedidos_libros"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    estudiante_id: Mapped[int] = mapped_column(ForeignKey("estudiantes.id"), nullable=False, index=True)
    libro_id: Mapped[int | None] = mapped_column(ForeignKey("libros.id"), nullable=True, index=True)
    titulo_solicitado: Mapped[str | None] = mapped_column(String(200), nullable=True)
    fecha_pedido: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now, index=True)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="pendiente", index=True)
    observacion: Mapped[str | None] = mapped_column(String(500), nullable=True)
    estudiante = relationship("Estudiante")
    libro = relationship("Libro")
