from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models import Asignacion, Asignatura, Profesor
from app.schemas import AsignacionCreate, AsignacionRead


def serialize_asignacion(asignacion: Asignacion) -> AsignacionRead:
    return AsignacionRead(
        id=asignacion.id,
        profesor_id=asignacion.profesor_id,
        asignatura_id=asignacion.asignatura_id,
        fecha_asignacion=asignacion.fecha_asignacion,
        profesor_nombre=f"{asignacion.profesor.nombre} {asignacion.profesor.apellido}",
        asignatura_nombre=asignacion.asignatura.nombre,
        asignatura_codigo=asignacion.asignatura.codigo,
    )


def list_asignaciones(db: Session) -> list[AsignacionRead]:
    asignaciones = (
        db.query(Asignacion)
        .options(joinedload(Asignacion.profesor), joinedload(Asignacion.asignatura))
        .order_by(Asignacion.fecha_asignacion.desc(), Asignacion.id.desc())
        .all()
    )
    return [serialize_asignacion(asignacion) for asignacion in asignaciones]


def create_asignacion(db: Session, payload: AsignacionCreate) -> AsignacionRead:
    profesor = db.get(Profesor, payload.profesor_id)
    if not profesor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profesor no encontrado.")
    asignatura = db.get(Asignatura, payload.asignatura_id)
    if not asignatura:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asignatura no encontrada.")

    asignacion = Asignacion(
        profesor_id=payload.profesor_id,
        asignatura_id=payload.asignatura_id,
        fecha_asignacion=payload.fecha_asignacion or date.today(),
    )
    db.add(asignacion)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La asignatura ya esta asignada a este profesor.",
        ) from exc
    db.refresh(asignacion)
    asignacion.profesor = profesor
    asignacion.asignatura = asignatura
    return serialize_asignacion(asignacion)


def delete_asignacion(db: Session, asignacion_id: int) -> None:
    asignacion = db.get(Asignacion, asignacion_id)
    if not asignacion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asignacion no encontrada.")
    db.delete(asignacion)
    db.commit()
