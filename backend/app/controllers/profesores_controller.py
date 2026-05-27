from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Asignacion, Profesor
from app.schemas import ProfesorCreate, ProfesorUpdate


def list_profesores(db: Session, search: str | None = None) -> list[Profesor]:
    query = db.query(Profesor)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Profesor.nombre.ilike(term),
                Profesor.apellido.ilike(term),
                Profesor.correo.ilike(term),
            )
        )
    return query.order_by(Profesor.apellido.asc(), Profesor.nombre.asc()).all()


def get_profesor(db: Session, profesor_id: int) -> Profesor:
    profesor = db.get(Profesor, profesor_id)
    if not profesor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profesor no encontrado.")
    return profesor


def create_profesor(db: Session, payload: ProfesorCreate) -> Profesor:
    profesor = Profesor(**payload.model_dump())
    db.add(profesor)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un profesor con ese correo.",
        ) from exc
    db.refresh(profesor)
    return profesor


def update_profesor(db: Session, profesor_id: int, payload: ProfesorUpdate) -> Profesor:
    profesor = get_profesor(db, profesor_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profesor, field, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un profesor con ese correo.",
        ) from exc
    db.refresh(profesor)
    return profesor


def delete_profesor(db: Session, profesor_id: int) -> None:
    profesor = get_profesor(db, profesor_id)
    has_asignaciones = db.query(Asignacion).filter(Asignacion.profesor_id == profesor_id).first()
    if has_asignaciones:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar el profesor porque tiene asignaciones asociadas.",
        )
    db.delete(profesor)
    db.commit()
