from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Asignacion, Asignatura
from app.schemas import AsignaturaCreate, AsignaturaUpdate


def list_asignaturas(db: Session, search: str | None = None) -> list[Asignatura]:
    query = db.query(Asignatura)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(or_(Asignatura.nombre.ilike(term), Asignatura.codigo.ilike(term)))
    return query.order_by(Asignatura.nombre.asc()).all()


def get_asignatura(db: Session, asignatura_id: int) -> Asignatura:
    asignatura = db.get(Asignatura, asignatura_id)
    if not asignatura:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asignatura no encontrada.")
    return asignatura


def create_asignatura(db: Session, payload: AsignaturaCreate) -> Asignatura:
    asignatura = Asignatura(**payload.model_dump())
    db.add(asignatura)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una asignatura con ese codigo.",
        ) from exc
    db.refresh(asignatura)
    return asignatura


def update_asignatura(db: Session, asignatura_id: int, payload: AsignaturaUpdate) -> Asignatura:
    asignatura = get_asignatura(db, asignatura_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(asignatura, field, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una asignatura con ese codigo.",
        ) from exc
    db.refresh(asignatura)
    return asignatura


def delete_asignatura(db: Session, asignatura_id: int) -> None:
    asignatura = get_asignatura(db, asignatura_id)
    has_asignaciones = db.query(Asignacion).filter(Asignacion.asignatura_id == asignatura_id).first()
    if has_asignaciones:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar la asignatura porque tiene asignaciones asociadas.",
        )
    db.delete(asignatura)
    db.commit()
