from collections import defaultdict
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models import Asignatura, Curso, Estudiante, Evaluacion, Nota, PeriodoAcademico, Profesor
from app.schemas.notas import (
    EstudianteCreate,
    EstudianteRead,
    EstudianteUpdate,
    EvaluacionCreate,
    EvaluacionRead,
    EvaluacionUpdate,
    NotaCreate,
    NotaRead,
    NotaResumenItem,
    NotaResumenRead,
    NotaUpdate,
    PeriodoAcademicoCreate,
    PeriodoAcademicoUpdate,
)


def _strip_strings(data: dict, fields: tuple[str, ...]) -> dict:
    for field in fields:
        if field in data and isinstance(data[field], str):
            data[field] = data[field].strip()
        if data.get(field) == "":
            data[field] = None
    return data


def _normalize_rut(value: str | None) -> str | None:
    if not value:
        return None
    return value.replace(".", "").replace(" ", "").upper()


def _nombre_profesor(profesor: Profesor | None) -> str | None:
    if not profesor:
        return None
    return f"{profesor.nombre} {profesor.apellido}"


def _nombre_estudiante(estudiante: Estudiante | None) -> str | None:
    if not estudiante:
        return None
    return f"{estudiante.nombre} {estudiante.apellido}"


def _to_float(value) -> float:
    return float(value or 0)


def _ensure_curso(db: Session, curso_id: int, require_active: bool = True) -> Curso:
    curso = db.get(Curso, curso_id)
    if not curso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso no encontrado.")
    if require_active and not curso.activo:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No se puede usar un curso inactivo.")
    return curso


def _ensure_profesor(db: Session, profesor_id: int, require_active: bool = True) -> Profesor:
    profesor = db.get(Profesor, profesor_id)
    if not profesor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profesor no encontrado.")
    if require_active and not profesor.activo:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No se puede usar un profesor inactivo.")
    return profesor


def _ensure_asignatura(db: Session, asignatura_id: int, require_active: bool = True) -> Asignatura:
    asignatura = db.get(Asignatura, asignatura_id)
    if not asignatura:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asignatura no encontrada.")
    if require_active and not asignatura.activo:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No se puede usar una asignatura inactiva.")
    return asignatura


def _ensure_periodo(db: Session, periodo_id: int, require_active: bool = True) -> PeriodoAcademico:
    periodo = db.get(PeriodoAcademico, periodo_id)
    if not periodo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Periodo academico no encontrado.")
    if require_active and not periodo.activo:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No se puede usar un periodo inactivo.")
    return periodo


def _ensure_estudiante(db: Session, estudiante_id: int, require_active: bool = True) -> Estudiante:
    estudiante = db.get(Estudiante, estudiante_id)
    if not estudiante:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudiante no encontrado.")
    if require_active and not estudiante.activo:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No se puede usar un estudiante inactivo.")
    return estudiante


def _get_evaluacion_query(db: Session):
    return db.query(Evaluacion).options(
        joinedload(Evaluacion.curso),
        joinedload(Evaluacion.asignatura),
        joinedload(Evaluacion.profesor),
        joinedload(Evaluacion.periodo),
    )


def get_evaluacion(db: Session, evaluacion_id: int) -> Evaluacion:
    evaluacion = _get_evaluacion_query(db).filter(Evaluacion.id == evaluacion_id).first()
    if not evaluacion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluacion no encontrada.")
    return evaluacion


def _validate_periodo_fechas(fecha_inicio, fecha_fin) -> None:
    if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La fecha fin debe ser mayor o igual que la fecha inicio.",
        )


def _validate_ponderacion_total(
    db: Session,
    curso_id: int,
    asignatura_id: int,
    periodo_id: int,
    anio_academico: int,
    ponderacion: float,
    estado_evaluacion: str,
    exclude_id: int | None = None,
) -> None:
    if estado_evaluacion != "activa":
        return
    query = db.query(Evaluacion).filter(
        Evaluacion.curso_id == curso_id,
        Evaluacion.asignatura_id == asignatura_id,
        Evaluacion.periodo_id == periodo_id,
        Evaluacion.anio_academico == anio_academico,
        Evaluacion.estado == "activa",
    )
    if exclude_id:
        query = query.filter(Evaluacion.id != exclude_id)
    total = sum(_to_float(item.ponderacion) for item in query.all()) + float(ponderacion)
    if total > 100:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La suma de ponderaciones activas no puede superar 100.",
        )


def _serialize_estudiante(estudiante: Estudiante) -> EstudianteRead:
    return EstudianteRead(
        id=estudiante.id,
        rut=estudiante.rut,
        nombre=estudiante.nombre,
        apellido=estudiante.apellido,
        correo=estudiante.correo,
        curso_id=estudiante.curso_id,
        anio_academico=estudiante.anio_academico,
        activo=estudiante.activo,
        curso_nombre=estudiante.curso.nombre if estudiante.curso else None,
    )


def list_estudiantes(
    db: Session,
    search: str | None = None,
    activo: bool | None = None,
    curso_id: int | None = None,
    anio_academico: int | None = None,
) -> list[EstudianteRead]:
    query = db.query(Estudiante).options(joinedload(Estudiante.curso))
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Estudiante.nombre.ilike(term),
                Estudiante.apellido.ilike(term),
                Estudiante.rut.ilike(term),
                Estudiante.correo.ilike(term),
            )
        )
    if activo is not None:
        query = query.filter(Estudiante.activo == activo)
    if curso_id:
        query = query.filter(Estudiante.curso_id == curso_id)
    if anio_academico:
        query = query.filter(Estudiante.anio_academico == anio_academico)
    estudiantes = query.order_by(Estudiante.apellido.asc(), Estudiante.nombre.asc()).all()
    return [_serialize_estudiante(estudiante) for estudiante in estudiantes]


def get_estudiante(db: Session, estudiante_id: int) -> EstudianteRead:
    estudiante = (
        db.query(Estudiante)
        .options(joinedload(Estudiante.curso))
        .filter(Estudiante.id == estudiante_id)
        .first()
    )
    if not estudiante:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudiante no encontrado.")
    return _serialize_estudiante(estudiante)


def create_estudiante(db: Session, payload: EstudianteCreate) -> EstudianteRead:
    data = _strip_strings(payload.model_dump(), ("rut", "nombre", "apellido", "correo"))
    data["rut"] = _normalize_rut(data.get("rut"))
    if data.get("correo"):
        data["correo"] = data["correo"].lower()
    _ensure_curso(db, data["curso_id"])
    estudiante = Estudiante(**data)
    db.add(estudiante)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un estudiante con ese RUT o correo.",
        ) from exc
    db.refresh(estudiante)
    return get_estudiante(db, estudiante.id)


def update_estudiante(db: Session, estudiante_id: int, payload: EstudianteUpdate) -> EstudianteRead:
    estudiante = _ensure_estudiante(db, estudiante_id, require_active=False)
    data = _strip_strings(payload.model_dump(exclude_unset=True), ("rut", "nombre", "apellido", "correo"))
    if "rut" in data:
        data["rut"] = _normalize_rut(data.get("rut"))
    if data.get("correo"):
        data["correo"] = data["correo"].lower()
    if "curso_id" in data and data["curso_id"] is not None:
        _ensure_curso(db, data["curso_id"])
    for field, value in data.items():
        setattr(estudiante, field, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un estudiante con ese RUT o correo.",
        ) from exc
    db.refresh(estudiante)
    return get_estudiante(db, estudiante.id)


def update_estudiante_estado(db: Session, estudiante_id: int, activo: bool) -> EstudianteRead:
    estudiante = _ensure_estudiante(db, estudiante_id, require_active=False)
    estudiante.activo = activo
    db.commit()
    db.refresh(estudiante)
    return get_estudiante(db, estudiante.id)


def delete_estudiante(db: Session, estudiante_id: int) -> None:
    estudiante = _ensure_estudiante(db, estudiante_id, require_active=False)
    if db.query(Nota).filter(Nota.estudiante_id == estudiante_id).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar el estudiante porque tiene notas asociadas.",
        )
    db.delete(estudiante)
    db.commit()


def list_periodos(
    db: Session,
    activo: bool | None = None,
    anio_academico: int | None = None,
) -> list[PeriodoAcademico]:
    query = db.query(PeriodoAcademico)
    if activo is not None:
        query = query.filter(PeriodoAcademico.activo == activo)
    if anio_academico:
        query = query.filter(PeriodoAcademico.anio_academico == anio_academico)
    return query.order_by(PeriodoAcademico.anio_academico.desc(), PeriodoAcademico.fecha_inicio.asc()).all()


def get_periodo(db: Session, periodo_id: int) -> PeriodoAcademico:
    return _ensure_periodo(db, periodo_id, require_active=False)


def create_periodo(db: Session, payload: PeriodoAcademicoCreate) -> PeriodoAcademico:
    data = _strip_strings(payload.model_dump(), ("nombre",))
    _validate_periodo_fechas(data["fecha_inicio"], data["fecha_fin"])
    periodo = PeriodoAcademico(**data)
    db.add(periodo)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un periodo con ese nombre y anio academico.",
        ) from exc
    db.refresh(periodo)
    return periodo


def update_periodo(db: Session, periodo_id: int, payload: PeriodoAcademicoUpdate) -> PeriodoAcademico:
    periodo = get_periodo(db, periodo_id)
    data = _strip_strings(payload.model_dump(exclude_unset=True), ("nombre",))
    fecha_inicio = data.get("fecha_inicio", periodo.fecha_inicio)
    fecha_fin = data.get("fecha_fin", periodo.fecha_fin)
    _validate_periodo_fechas(fecha_inicio, fecha_fin)
    for field, value in data.items():
        setattr(periodo, field, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un periodo con ese nombre y anio academico.",
        ) from exc
    db.refresh(periodo)
    return periodo


def delete_periodo(db: Session, periodo_id: int) -> None:
    periodo = get_periodo(db, periodo_id)
    if db.query(Evaluacion).filter(Evaluacion.periodo_id == periodo_id).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar el periodo porque tiene evaluaciones asociadas.",
        )
    db.delete(periodo)
    db.commit()


def _serialize_evaluacion(evaluacion: Evaluacion) -> EvaluacionRead:
    return EvaluacionRead(
        id=evaluacion.id,
        titulo=evaluacion.titulo,
        descripcion=evaluacion.descripcion,
        curso_id=evaluacion.curso_id,
        asignatura_id=evaluacion.asignatura_id,
        profesor_id=evaluacion.profesor_id,
        periodo_id=evaluacion.periodo_id,
        fecha=evaluacion.fecha,
        ponderacion=_to_float(evaluacion.ponderacion),
        anio_academico=evaluacion.anio_academico,
        estado=evaluacion.estado,
        curso_nombre=evaluacion.curso.nombre if evaluacion.curso else None,
        asignatura_nombre=evaluacion.asignatura.nombre if evaluacion.asignatura else None,
        profesor_nombre=_nombre_profesor(evaluacion.profesor),
        periodo_nombre=evaluacion.periodo.nombre if evaluacion.periodo else None,
        notas_registradas=len(evaluacion.notas),
    )


def list_evaluaciones(
    db: Session,
    anio_academico: int | None = None,
    curso_id: int | None = None,
    profesor_id: int | None = None,
    asignatura_id: int | None = None,
    periodo_id: int | None = None,
    estado: str | None = None,
) -> list[EvaluacionRead]:
    query = _get_evaluacion_query(db).options(joinedload(Evaluacion.notas))
    if anio_academico:
        query = query.filter(Evaluacion.anio_academico == anio_academico)
    if curso_id:
        query = query.filter(Evaluacion.curso_id == curso_id)
    if profesor_id:
        query = query.filter(Evaluacion.profesor_id == profesor_id)
    if asignatura_id:
        query = query.filter(Evaluacion.asignatura_id == asignatura_id)
    if periodo_id:
        query = query.filter(Evaluacion.periodo_id == periodo_id)
    if estado:
        query = query.filter(Evaluacion.estado == estado)
    evaluaciones = query.order_by(Evaluacion.fecha.desc(), Evaluacion.id.desc()).all()
    return [_serialize_evaluacion(evaluacion) for evaluacion in evaluaciones]


def get_evaluacion_read(db: Session, evaluacion_id: int) -> EvaluacionRead:
    return _serialize_evaluacion(get_evaluacion(db, evaluacion_id))


def _validate_evaluacion_refs(db: Session, data: dict, require_active: bool = True) -> None:
    curso = _ensure_curso(db, data["curso_id"], require_active=require_active)
    periodo = _ensure_periodo(db, data["periodo_id"], require_active=require_active)
    _ensure_profesor(db, data["profesor_id"], require_active=require_active)
    _ensure_asignatura(db, data["asignatura_id"], require_active=require_active)
    if periodo.anio_academico != data["anio_academico"] or curso.anio_academico != data["anio_academico"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El curso y el periodo deben pertenecer al mismo anio academico de la evaluacion.",
        )


def create_evaluacion(db: Session, payload: EvaluacionCreate) -> EvaluacionRead:
    data = _strip_strings(payload.model_dump(), ("titulo", "descripcion", "estado"))
    _validate_evaluacion_refs(db, data)
    _validate_ponderacion_total(
        db,
        data["curso_id"],
        data["asignatura_id"],
        data["periodo_id"],
        data["anio_academico"],
        data["ponderacion"],
        data["estado"],
    )
    evaluacion = Evaluacion(**data)
    db.add(evaluacion)
    db.commit()
    db.refresh(evaluacion)
    return get_evaluacion_read(db, evaluacion.id)


def update_evaluacion(db: Session, evaluacion_id: int, payload: EvaluacionUpdate) -> EvaluacionRead:
    evaluacion = get_evaluacion(db, evaluacion_id)
    data = _strip_strings(payload.model_dump(exclude_unset=True), ("titulo", "descripcion", "estado"))
    changed_refs = any(field in data for field in ("curso_id", "asignatura_id", "profesor_id", "periodo_id", "anio_academico"))
    next_values = {
        "curso_id": data.get("curso_id", evaluacion.curso_id),
        "asignatura_id": data.get("asignatura_id", evaluacion.asignatura_id),
        "profesor_id": data.get("profesor_id", evaluacion.profesor_id),
        "periodo_id": data.get("periodo_id", evaluacion.periodo_id),
        "anio_academico": data.get("anio_academico", evaluacion.anio_academico),
        "ponderacion": data.get("ponderacion", _to_float(evaluacion.ponderacion)),
        "estado": data.get("estado", evaluacion.estado),
    }
    _validate_evaluacion_refs(db, next_values, require_active=changed_refs)
    _validate_ponderacion_total(
        db,
        next_values["curso_id"],
        next_values["asignatura_id"],
        next_values["periodo_id"],
        next_values["anio_academico"],
        next_values["ponderacion"],
        next_values["estado"],
        exclude_id=evaluacion_id,
    )
    for field, value in data.items():
        setattr(evaluacion, field, value)
    db.commit()
    db.refresh(evaluacion)
    return get_evaluacion_read(db, evaluacion.id)


def update_evaluacion_estado(db: Session, evaluacion_id: int, estado_evaluacion: str) -> EvaluacionRead:
    return update_evaluacion(db, evaluacion_id, EvaluacionUpdate(estado=estado_evaluacion))


def delete_evaluacion(db: Session, evaluacion_id: int) -> None:
    evaluacion = get_evaluacion(db, evaluacion_id)
    if db.query(Nota).filter(Nota.evaluacion_id == evaluacion_id).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar la evaluacion porque tiene notas asociadas.",
        )
    db.delete(evaluacion)
    db.commit()


def _serialize_nota(nota: Nota) -> NotaRead:
    evaluacion = nota.evaluacion
    estudiante = nota.estudiante
    return NotaRead(
        id=nota.id,
        estudiante_id=nota.estudiante_id,
        evaluacion_id=nota.evaluacion_id,
        nota=_to_float(nota.nota),
        observacion=nota.observacion,
        fecha_registro=nota.fecha_registro,
        estudiante_nombre=_nombre_estudiante(estudiante),
        evaluacion_titulo=evaluacion.titulo if evaluacion else None,
        curso_nombre=evaluacion.curso.nombre if evaluacion and evaluacion.curso else None,
        asignatura_nombre=evaluacion.asignatura.nombre if evaluacion and evaluacion.asignatura else None,
        profesor_nombre=_nombre_profesor(evaluacion.profesor) if evaluacion else None,
        periodo_nombre=evaluacion.periodo.nombre if evaluacion and evaluacion.periodo else None,
        ponderacion=_to_float(evaluacion.ponderacion) if evaluacion else None,
    )


def serialize_nota(nota: Nota) -> NotaRead:
    return _serialize_nota(nota)


def _get_nota_query(db: Session):
    return db.query(Nota).options(
        joinedload(Nota.estudiante),
        joinedload(Nota.evaluacion).joinedload(Evaluacion.curso),
        joinedload(Nota.evaluacion).joinedload(Evaluacion.asignatura),
        joinedload(Nota.evaluacion).joinedload(Evaluacion.profesor),
        joinedload(Nota.evaluacion).joinedload(Evaluacion.periodo),
    )


def list_notas(
    db: Session,
    estudiante_id: int | None = None,
    evaluacion_id: int | None = None,
    curso_id: int | None = None,
    asignatura_id: int | None = None,
    profesor_id: int | None = None,
    periodo_id: int | None = None,
    anio_academico: int | None = None,
) -> list[NotaRead]:
    query = _get_nota_query(db).join(Nota.evaluacion)
    if estudiante_id:
        query = query.filter(Nota.estudiante_id == estudiante_id)
    if evaluacion_id:
        query = query.filter(Nota.evaluacion_id == evaluacion_id)
    if curso_id:
        query = query.filter(Evaluacion.curso_id == curso_id)
    if asignatura_id:
        query = query.filter(Evaluacion.asignatura_id == asignatura_id)
    if profesor_id:
        query = query.filter(Evaluacion.profesor_id == profesor_id)
    if periodo_id:
        query = query.filter(Evaluacion.periodo_id == periodo_id)
    if anio_academico:
        query = query.filter(Evaluacion.anio_academico == anio_academico)
    notas = query.order_by(Nota.fecha_registro.desc(), Nota.id.desc()).all()
    return [_serialize_nota(nota) for nota in notas]


def get_nota(db: Session, nota_id: int) -> Nota:
    nota = _get_nota_query(db).filter(Nota.id == nota_id).first()
    if not nota:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nota no encontrada.")
    return nota


def _validate_nota_relation(estudiante: Estudiante, evaluacion: Evaluacion) -> None:
    if estudiante.curso_id != evaluacion.curso_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El estudiante no pertenece al curso de la evaluacion.",
        )
    if estudiante.anio_academico != evaluacion.anio_academico:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El estudiante no pertenece al anio academico de la evaluacion.",
        )


def create_or_update_nota(db: Session, payload: NotaCreate) -> NotaRead:
    data = _strip_strings(payload.model_dump(), ("observacion",))
    estudiante = _ensure_estudiante(db, data["estudiante_id"])
    evaluacion = get_evaluacion(db, data["evaluacion_id"])
    if evaluacion.estado == "cancelada":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No se puede registrar nota en una evaluacion cancelada.")
    _validate_nota_relation(estudiante, evaluacion)
    nota = (
        db.query(Nota)
        .filter(Nota.estudiante_id == data["estudiante_id"], Nota.evaluacion_id == data["evaluacion_id"])
        .first()
    )
    if nota:
        nota.nota = Decimal(str(data["nota"]))
        nota.observacion = data.get("observacion")
    else:
        nota = Nota(**data)
        db.add(nota)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una nota para ese estudiante y evaluacion.",
        ) from exc
    db.refresh(nota)
    return _serialize_nota(get_nota(db, nota.id))


def update_nota(db: Session, nota_id: int, payload: NotaUpdate) -> NotaRead:
    nota = get_nota(db, nota_id)
    data = _strip_strings(payload.model_dump(exclude_unset=True), ("observacion",))
    if "nota" in data and data["nota"] is not None:
        nota.nota = Decimal(str(data["nota"]))
    if "observacion" in data:
        nota.observacion = data["observacion"]
    db.commit()
    db.refresh(nota)
    return _serialize_nota(get_nota(db, nota.id))


def delete_nota(db: Session, nota_id: int) -> None:
    nota = get_nota(db, nota_id)
    db.delete(nota)
    db.commit()


def get_notas_resumen(
    db: Session,
    curso_id: int | None = None,
    asignatura_id: int | None = None,
    estudiante_id: int | None = None,
    periodo_id: int | None = None,
    anio_academico: int | None = None,
) -> NotaResumenRead:
    query = _get_nota_query(db).join(Nota.evaluacion).join(Nota.estudiante)
    if curso_id:
        query = query.filter(Evaluacion.curso_id == curso_id)
    if asignatura_id:
        query = query.filter(Evaluacion.asignatura_id == asignatura_id)
    if estudiante_id:
        query = query.filter(Nota.estudiante_id == estudiante_id)
    if periodo_id:
        query = query.filter(Evaluacion.periodo_id == periodo_id)
    if anio_academico:
        query = query.filter(Evaluacion.anio_academico == anio_academico)

    groups = defaultdict(list)
    total_weighted = 0.0
    total_weight = 0.0
    for nota in query.all():
        evaluacion = nota.evaluacion
        estudiante = nota.estudiante
        key = (estudiante.id, evaluacion.curso_id, evaluacion.asignatura_id, evaluacion.periodo_id, evaluacion.anio_academico)
        groups[key].append(nota)
        weight = _to_float(evaluacion.ponderacion)
        if weight > 0:
            total_weighted += _to_float(nota.nota) * weight
            total_weight += weight

    items: list[NotaResumenItem] = []
    for notas in groups.values():
        first = notas[0]
        evaluacion = first.evaluacion
        estudiante = first.estudiante
        ponderacion_total = sum(_to_float(item.evaluacion.ponderacion) for item in notas)
        promedio = None
        if ponderacion_total > 0:
            promedio = round(
                sum(_to_float(item.nota) * _to_float(item.evaluacion.ponderacion) for item in notas) / ponderacion_total,
                1,
            )
        items.append(
            NotaResumenItem(
                estudiante_id=estudiante.id,
                estudiante_nombre=_nombre_estudiante(estudiante) or "",
                curso_id=evaluacion.curso_id,
                curso_nombre=evaluacion.curso.nombre,
                asignatura_id=evaluacion.asignatura_id,
                asignatura_nombre=evaluacion.asignatura.nombre,
                periodo_id=evaluacion.periodo_id,
                periodo_nombre=evaluacion.periodo.nombre,
                anio_academico=evaluacion.anio_academico,
                promedio=promedio,
                notas_registradas=len(notas),
                ponderacion_registrada=round(ponderacion_total, 2),
            )
        )

    items.sort(key=lambda item: (item.curso_nombre, item.asignatura_nombre, item.estudiante_nombre))
    promedio_general = round(total_weighted / total_weight, 1) if total_weight else None
    return NotaResumenRead(promedio_general=promedio_general, items=items)
