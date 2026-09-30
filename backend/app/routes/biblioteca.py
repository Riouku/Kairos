from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Literal
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import Estudiante
from app.models.biblioteca import Libro, PedidoLibro, PrestamoLibro

router = APIRouter(prefix="/biblioteca", tags=["Biblioteca"])
class LibroIn(BaseModel):
    titulo: str = Field(min_length=1, max_length=200)
    autor: str = Field(min_length=1, max_length=150)
    isbn: str | None = None
    ejemplares: int = Field(default=1, ge=1)
class PedidoIn(BaseModel):
    estudiante_id: int
    libro_id: int | None = None
    titulo_solicitado: str | None = Field(default=None, min_length=1, max_length=200)
    observacion: str | None = Field(default=None, max_length=500)
    @model_validator(mode="after")
    def validar_libro(self):
        if self.libro_id is None and not (self.titulo_solicitado or "").strip():
            raise ValueError("Selecciona un libro o escribe el título solicitado.")
        return self
class PedidoEstadoIn(BaseModel):
    estado: Literal["pendiente", "aprobado", "rechazado", "entregado"]
class PrestamoIn(BaseModel):
    libro_id: int
    estudiante_id: int
    fecha_prestamo: date = Field(default_factory=date.today)
    fecha_devolucion: date

@router.get("/libros")
def libros(db: Session = Depends(get_db)):
    return [{"id": x.id, "titulo": x.titulo, "autor": x.autor, "isbn": x.isbn, "ejemplares": x.ejemplares, "disponibles": max(0, x.ejemplares-sum(1 for p in x.prestamos if p.devuelto_en is None))} for x in db.query(Libro).order_by(Libro.titulo).all()]
@router.post("/libros", status_code=201)
def crear_libro(data: LibroIn, db: Session = Depends(get_db)):
    values=data.model_dump(); values["isbn"]=(values["isbn"] or "").strip() or None
    item=Libro(**values); db.add(item); db.commit(); db.refresh(item); return item
@router.get("/prestamos")
def prestamos(pendientes: bool=False, db: Session=Depends(get_db)):
    q=db.query(PrestamoLibro).options(joinedload(PrestamoLibro.libro), joinedload(PrestamoLibro.estudiante))
    if pendientes: q=q.filter(PrestamoLibro.devuelto_en.is_(None))
    return [{"id":p.id,"libro_id":p.libro_id,"estudiante_id":p.estudiante_id,"libro":p.libro.titulo,"estudiante":p.estudiante.nombre+" "+p.estudiante.apellido,"fecha_prestamo":p.fecha_prestamo,"fecha_devolucion":p.fecha_devolucion,"devuelto_en":p.devuelto_en,"vencido":p.devuelto_en is None and p.fecha_devolucion<date.today()} for p in q.order_by(PrestamoLibro.fecha_devolucion).all()]
@router.post("/prestamos", status_code=201)
def crear_prestamo(data: PrestamoIn, db: Session=Depends(get_db)):
    libro=db.get(Libro,data.libro_id); estudiante=db.get(Estudiante,data.estudiante_id)
    if not libro or not estudiante: raise HTTPException(404,"Libro o estudiante no encontrado.")
    if not estudiante.activo: raise HTTPException(409,"El estudiante está inactivo.")
    if data.fecha_devolucion<data.fecha_prestamo: raise HTTPException(422,"La devolución debe ser posterior al préstamo.")
    activos=db.query(PrestamoLibro).filter(PrestamoLibro.libro_id==libro.id,PrestamoLibro.devuelto_en.is_(None)).count()
    if activos>=libro.ejemplares: raise HTTPException(409,"No hay ejemplares disponibles.")
    p=PrestamoLibro(**data.model_dump()); db.add(p); db.commit(); db.refresh(p); return {"id":p.id}
@router.patch("/prestamos/{prestamo_id}/devolver")
def devolver(prestamo_id:int, db:Session=Depends(get_db)):
    p=db.get(PrestamoLibro,prestamo_id)
    if not p: raise HTTPException(404,"Préstamo no encontrado.")
    if p.devuelto_en: raise HTTPException(409,"El libro ya fue devuelto.")
    p.devuelto_en=datetime.now(); db.commit(); return {"id":p.id,"devuelto_en":p.devuelto_en}


@router.get("/pedidos")
def pedidos(estado: str | None = None, db: Session = Depends(get_db)):
    q = db.query(PedidoLibro).options(joinedload(PedidoLibro.estudiante), joinedload(PedidoLibro.libro))
    if estado:
        q = q.filter(PedidoLibro.estado == estado)
    return [{"id":p.id,"estudiante_id":p.estudiante_id,"estudiante":p.estudiante.nombre+" "+p.estudiante.apellido,
        "libro_id":p.libro_id,"titulo":p.libro.titulo if p.libro else p.titulo_solicitado,
        "fecha_pedido":p.fecha_pedido,"estado":p.estado,"observacion":p.observacion}
        for p in q.order_by(PedidoLibro.fecha_pedido.desc()).all()]

@router.post("/pedidos", status_code=201)
def crear_pedido(data: PedidoIn, db: Session = Depends(get_db)):
    estudiante = db.get(Estudiante, data.estudiante_id)
    if not estudiante or not estudiante.activo:
        raise HTTPException(404, "Estudiante activo no encontrado.")
    if data.libro_id is not None and not db.get(Libro, data.libro_id):
        raise HTTPException(404, "Libro no encontrado.")
    values = data.model_dump()
    values["titulo_solicitado"] = (values["titulo_solicitado"] or "").strip() or None
    item = PedidoLibro(**values)
    db.add(item); db.commit(); db.refresh(item)
    return {"id":item.id,"estado":item.estado,"fecha_pedido":item.fecha_pedido}

@router.patch("/pedidos/{pedido_id}")
def actualizar_pedido(pedido_id: int, data: PedidoEstadoIn, db: Session = Depends(get_db)):
    item = db.get(PedidoLibro, pedido_id)
    if not item:
        raise HTTPException(404, "Pedido no encontrado.")
    item.estado = data.estado
    db.commit()
    return {"id":item.id,"estado":item.estado}
