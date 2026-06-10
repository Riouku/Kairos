from calendar import monthrange
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models import Asistencia, Curso, Estudiante
from app.schemas import (
    AsistenciaBulkCreate,
    AsistenciaCreate,
    AsistenciaRead,
    AsistenciaResumenRead,
    AsistenciaUpdate,
)


def _nombre_estudiante(estudiante: Estudiante | None) -> str | None:
    if not estudiante:
        return None
    return f"{estudiante.nombre} {estudiante.apellido}"


def _serialize_asistencia(asistencia: Asistencia) -> AsistenciaRead:
    return AsistenciaRead(
        id=asistencia.id,
        estudiante_id=asistencia.estudiante_id,
        curso_id=asistencia.curso_id,
        fecha=asistencia.fecha,
        estado=asistencia.estado,
        observacion=asistencia.observacion,
        anio_academico=asistencia.anio_academico,
        fecha_registro=asistencia.fecha_registro,
        estudiante_nombre=_nombre_estudiante(asistencia.estudiante),
        curso_nombre=asistencia.curso.nombre if asistencia.curso else None,
    )


def _ensure_curso(db: Session, curso_id: int) -> Curso:
    curso = db.get(Curso, curso_id)
    if not curso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso no encontrado.")
    if not curso.activo:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No se puede registrar asistencia en un curso inactivo.")
    return curso


def _ensure_estudiante_en_curso(db: Session, estudiante_id: int, curso_id: int, anio_academico: int) -> Estudiante:
    estudiante = db.get(Estudiante, estudiante_id)
    if not estudiante:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudiante no encontrado.")
    if not estudiante.activo:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No se puede registrar asistencia de un estudiante inactivo.")
    if estudiante.curso_id != curso_id or estudiante.anio_academico != anio_academico:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El estudiante no pertenece al curso y año académico seleccionados.")
    return estudiante


def list_asistencias(
    db: Session,
    curso_id: int | None = None,
    estudiante_id: int | None = None,
    fecha: date | None = None,
    mes: int | None = None,
    anio_academico: int | None = None,
) -> list[AsistenciaRead]:
    query = db.query(Asistencia).options(joinedload(Asistencia.estudiante), joinedload(Asistencia.curso))
    if curso_id:
        query = query.filter(Asistencia.curso_id == curso_id)
    if estudiante_id:
        query = query.filter(Asistencia.estudiante_id == estudiante_id)
    if fecha:
        query = query.filter(Asistencia.fecha == fecha)
    if anio_academico:
        query = query.filter(Asistencia.anio_academico == anio_academico)
    if mes and anio_academico:
        _, last_day = monthrange(anio_academico, mes)
        query = query.filter(Asistencia.fecha.between(date(anio_academico, mes, 1), date(anio_academico, mes, last_day)))
    asistencias = query.order_by(Asistencia.fecha.desc(), Asistencia.id.desc()).all()
    return [_serialize_asistencia(asistencia) for asistencia in asistencias]


def get_asistencia(db: Session, asistencia_id: int) -> AsistenciaRead:
    asistencia = (
        db.query(Asistencia)
        .options(joinedload(Asistencia.estudiante), joinedload(Asistencia.curso))
        .filter(Asistencia.id == asistencia_id)
        .first()
    )
    if not asistencia:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asistencia no encontrada.")
    return _serialize_asistencia(asistencia)


def create_or_update_asistencia(db: Session, payload: AsistenciaCreate) -> AsistenciaRead:
    _ensure_curso(db, payload.curso_id)
    _ensure_estudiante_en_curso(db, payload.estudiante_id, payload.curso_id, payload.anio_academico)
    asistencia = (
        db.query(Asistencia)
        .filter(Asistencia.estudiante_id == payload.estudiante_id, Asistencia.fecha == payload.fecha)
        .first()
    )
    if asistencia:
        asistencia.estado = payload.estado
        asistencia.observacion = payload.observacion
        asistencia.curso_id = payload.curso_id
        asistencia.anio_academico = payload.anio_academico
    else:
        asistencia = Asistencia(**payload.model_dump())
        db.add(asistencia)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe asistencia para ese estudiante y fecha.") from exc
    db.refresh(asistencia)
    return get_asistencia(db, asistencia.id)


def create_or_update_asistencias_bulk(db: Session, payload: AsistenciaBulkCreate) -> list[AsistenciaRead]:
    _ensure_curso(db, payload.curso_id)
    resultados: list[AsistenciaRead] = []
    for item in payload.registros:
        registro = AsistenciaCreate(
            estudiante_id=item.estudiante_id,
            curso_id=payload.curso_id,
            fecha=payload.fecha,
            estado=item.estado,
            observacion=item.observacion,
            anio_academico=payload.anio_academico,
        )
        resultados.append(create_or_update_asistencia(db, registro))
    return resultados


def update_asistencia(db: Session, asistencia_id: int, payload: AsistenciaUpdate) -> AsistenciaRead:
    asistencia = db.get(Asistencia, asistencia_id)
    if not asistencia:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asistencia no encontrada.")
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(asistencia, field, value)
    db.commit()
    db.refresh(asistencia)
    return get_asistencia(db, asistencia.id)


def delete_asistencia(db: Session, asistencia_id: int) -> None:
    asistencia = db.get(Asistencia, asistencia_id)
    if not asistencia:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asistencia no encontrada.")
    db.delete(asistencia)
    db.commit()


def get_asistencia_resumen(db: Session, curso_id: int | None, mes: int, anio_academico: int) -> AsistenciaResumenRead:
    if mes < 1 or mes > 12:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El mes debe estar entre 1 y 12.")
    _, last_day = monthrange(anio_academico, mes)
    query = db.query(Asistencia).filter(
        Asistencia.anio_academico == anio_academico,
        Asistencia.fecha.between(date(anio_academico, mes, 1), date(anio_academico, mes, last_day)),
    )
    if curso_id:
        query = query.filter(Asistencia.curso_id == curso_id)
    registros = query.all()
    total = len(registros)
    presentes = sum(1 for item in registros if item.estado == "presente")
    ausentes = sum(1 for item in registros if item.estado == "ausente")
    tardes = sum(1 for item in registros if item.estado == "tarde")
    justificados = sum(1 for item in registros if item.estado == "justificado")
    asistidos = presentes + tardes + justificados
    porcentaje = round((asistidos / total) * 100, 1) if total else None
    return AsistenciaResumenRead(
        curso_id=curso_id,
        mes=mes,
        anio_academico=anio_academico,
        total_registros=total,
        presentes=presentes,
        ausentes=ausentes,
        tardes=tardes,
        justificados=justificados,
        porcentaje_asistencia=porcentaje,
    )
