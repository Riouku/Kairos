from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Asignacion, Asignatura, HorarioClase
from app.schemas import AsignaturaCreate, AsignaturaUpdate


def normalize_asignatura_payload(data: dict) -> dict:
    for field in ("nombre", "codigo", "nivel", "descripcion"):
        if field in data and isinstance(data[field], str):
            data[field] = data[field].strip()
    for field in ("nivel", "descripcion"):
        if data.get(field) == "":
            data[field] = None
    if data.get("codigo"):
        data["codigo"] = data["codigo"].upper()
    return data


def list_asignaturas(
    db: Session,
    search: str | None = None,
    activo: bool | None = None,
    nivel: str | None = None,
) -> list[Asignatura]:
    query = db.query(Asignatura)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Asignatura.nombre.ilike(term),
                Asignatura.codigo.ilike(term),
                Asignatura.nivel.ilike(term),
                Asignatura.descripcion.ilike(term),
            )
        )
    if activo is not None:
        query = query.filter(Asignatura.activo == activo)
    if nivel:
        query = query.filter(Asignatura.nivel.ilike(nivel.strip()))
    return query.order_by(Asignatura.nombre.asc()).all()


def get_asignatura(db: Session, asignatura_id: int) -> Asignatura:
    asignatura = db.get(Asignatura, asignatura_id)
    if not asignatura:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asignatura no encontrada.")
    return asignatura


def create_asignatura(db: Session, payload: AsignaturaCreate) -> Asignatura:
    asignatura = Asignatura(**normalize_asignatura_payload(payload.model_dump()))
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
    for field, value in normalize_asignatura_payload(payload.model_dump(exclude_unset=True)).items():
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


def update_asignatura_estado(db: Session, asignatura_id: int, activo: bool) -> Asignatura:
    asignatura = get_asignatura(db, asignatura_id)
    asignatura.activo = activo
    db.commit()
    db.refresh(asignatura)
    return asignatura


def delete_asignatura(db: Session, asignatura_id: int) -> None:
    asignatura = get_asignatura(db, asignatura_id)
    has_asignaciones = db.query(Asignacion).filter(Asignacion.asignatura_id == asignatura_id).first()
    has_horarios = db.query(HorarioClase).filter(HorarioClase.asignatura_id == asignatura_id).first()
    if has_asignaciones or has_horarios:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar la asignatura porque tiene asignaciones u horarios asociados.",
        )
    db.delete(asignatura)
    db.commit()
