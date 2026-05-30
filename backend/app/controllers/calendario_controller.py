from calendar import monthrange
from datetime import date, datetime, time, timedelta

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models import Asignatura, Curso, EventoAcademico, HorarioClase, Profesor
from app.schemas import (
    CalendarioItem,
    CalendarioMesRead,
    CursoCreate,
    CursoUpdate,
    EventoAcademicoCreate,
    EventoAcademicoRead,
    EventoAcademicoUpdate,
    HorarioClaseCreate,
    HorarioClaseRead,
    HorarioClaseUpdate,
)


def _strip_strings(data: dict, fields: tuple[str, ...]) -> dict:
    for field in fields:
        if field in data and isinstance(data[field], str):
            data[field] = data[field].strip()
        if data.get(field) == "":
            data[field] = None
    return data


def _nombre_profesor(profesor: Profesor | None) -> str | None:
    if not profesor:
        return None
    return f"{profesor.nombre} {profesor.apellido}"


def _validate_evento_fechas(fecha_inicio: datetime, fecha_fin: datetime | None) -> None:
    if fecha_fin and fecha_fin <= fecha_inicio:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La fecha fin debe ser mayor que la fecha inicio.",
        )


def _validate_horas(hora_inicio: time, hora_fin: time) -> None:
    if hora_fin <= hora_inicio:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La hora fin debe ser mayor que la hora inicio.",
        )


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


def serialize_curso(curso: Curso) -> Curso:
    return curso


def list_cursos(
    db: Session,
    search: str | None = None,
    activo: bool | None = None,
    anio_academico: int | None = None,
) -> list[Curso]:
    query = db.query(Curso)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(or_(Curso.nombre.ilike(term), Curso.nivel.ilike(term), Curso.letra.ilike(term)))
    if activo is not None:
        query = query.filter(Curso.activo == activo)
    if anio_academico:
        query = query.filter(Curso.anio_academico == anio_academico)
    return query.order_by(Curso.anio_academico.desc(), Curso.nivel.asc(), Curso.letra.asc()).all()


def get_curso(db: Session, curso_id: int) -> Curso:
    return _ensure_curso(db, curso_id, require_active=False)


def create_curso(db: Session, payload: CursoCreate) -> Curso:
    data = _strip_strings(payload.model_dump(), ("nombre", "nivel", "letra", "jornada"))
    if data.get("letra"):
        data["letra"] = data["letra"].upper()
    curso = Curso(**data)
    db.add(curso)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un curso con ese nombre, jornada y anio academico.",
        ) from exc
    db.refresh(curso)
    return curso


def update_curso(db: Session, curso_id: int, payload: CursoUpdate) -> Curso:
    curso = get_curso(db, curso_id)
    data = _strip_strings(payload.model_dump(exclude_unset=True), ("nombre", "nivel", "letra", "jornada"))
    if data.get("letra"):
        data["letra"] = data["letra"].upper()
    for field, value in data.items():
        setattr(curso, field, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un curso con ese nombre, jornada y anio academico.",
        ) from exc
    db.refresh(curso)
    return curso


def delete_curso(db: Session, curso_id: int) -> None:
    curso = get_curso(db, curso_id)
    has_eventos = db.query(EventoAcademico).filter(EventoAcademico.curso_id == curso_id).first()
    has_horarios = db.query(HorarioClase).filter(HorarioClase.curso_id == curso_id).first()
    if has_eventos or has_horarios:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar el curso porque tiene eventos u horarios asociados.",
        )
    db.delete(curso)
    db.commit()


def _serialize_evento(evento: EventoAcademico) -> EventoAcademicoRead:
    return EventoAcademicoRead(
        id=evento.id,
        titulo=evento.titulo,
        descripcion=evento.descripcion,
        fecha_inicio=evento.fecha_inicio,
        fecha_fin=evento.fecha_fin,
        tipo=evento.tipo,
        curso_id=evento.curso_id,
        profesor_id=evento.profesor_id,
        asignatura_id=evento.asignatura_id,
        anio_academico=evento.anio_academico,
        estado=evento.estado,
        curso_nombre=evento.curso.nombre if evento.curso else None,
        profesor_nombre=_nombre_profesor(evento.profesor),
        asignatura_nombre=evento.asignatura.nombre if evento.asignatura else None,
    )


def list_eventos(
    db: Session,
    anio_academico: int | None = None,
    tipo: str | None = None,
    curso_id: int | None = None,
    profesor_id: int | None = None,
    asignatura_id: int | None = None,
) -> list[EventoAcademicoRead]:
    query = db.query(EventoAcademico).options(
        joinedload(EventoAcademico.curso),
        joinedload(EventoAcademico.profesor),
        joinedload(EventoAcademico.asignatura),
    )
    if anio_academico:
        query = query.filter(EventoAcademico.anio_academico == anio_academico)
    if tipo:
        query = query.filter(EventoAcademico.tipo == tipo)
    if curso_id:
        query = query.filter(EventoAcademico.curso_id == curso_id)
    if profesor_id:
        query = query.filter(EventoAcademico.profesor_id == profesor_id)
    if asignatura_id:
        query = query.filter(EventoAcademico.asignatura_id == asignatura_id)
    eventos = query.order_by(EventoAcademico.fecha_inicio.asc(), EventoAcademico.id.asc()).all()
    return [_serialize_evento(evento) for evento in eventos]


def get_evento(db: Session, evento_id: int) -> EventoAcademico:
    evento = (
        db.query(EventoAcademico)
        .options(joinedload(EventoAcademico.curso), joinedload(EventoAcademico.profesor), joinedload(EventoAcademico.asignatura))
        .filter(EventoAcademico.id == evento_id)
        .first()
    )
    if not evento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento academico no encontrado.")
    return evento


def create_evento(db: Session, payload: EventoAcademicoCreate) -> EventoAcademicoRead:
    data = _strip_strings(payload.model_dump(), ("titulo", "descripcion", "tipo", "estado"))
    _validate_evento_fechas(data["fecha_inicio"], data.get("fecha_fin"))
    if data.get("curso_id"):
        _ensure_curso(db, data["curso_id"])
    if data.get("profesor_id"):
        _ensure_profesor(db, data["profesor_id"])
    if data.get("asignatura_id"):
        _ensure_asignatura(db, data["asignatura_id"])
    evento = EventoAcademico(**data)
    db.add(evento)
    db.commit()
    db.refresh(evento)
    return _serialize_evento(get_evento(db, evento.id))


def update_evento(db: Session, evento_id: int, payload: EventoAcademicoUpdate) -> EventoAcademicoRead:
    evento = get_evento(db, evento_id)
    data = _strip_strings(payload.model_dump(exclude_unset=True), ("titulo", "descripcion", "tipo", "estado"))
    fecha_inicio = data.get("fecha_inicio", evento.fecha_inicio)
    fecha_fin = data.get("fecha_fin", evento.fecha_fin)
    _validate_evento_fechas(fecha_inicio, fecha_fin)
    if "curso_id" in data and data["curso_id"] is not None:
        _ensure_curso(db, data["curso_id"])
    if "profesor_id" in data and data["profesor_id"] is not None:
        _ensure_profesor(db, data["profesor_id"])
    if "asignatura_id" in data and data["asignatura_id"] is not None:
        _ensure_asignatura(db, data["asignatura_id"])
    for field, value in data.items():
        setattr(evento, field, value)
    db.commit()
    db.refresh(evento)
    return _serialize_evento(get_evento(db, evento.id))


def delete_evento(db: Session, evento_id: int) -> None:
    evento = get_evento(db, evento_id)
    db.delete(evento)
    db.commit()


def _serialize_horario(horario: HorarioClase) -> HorarioClaseRead:
    return HorarioClaseRead(
        id=horario.id,
        curso_id=horario.curso_id,
        profesor_id=horario.profesor_id,
        asignatura_id=horario.asignatura_id,
        dia_semana=horario.dia_semana,
        hora_inicio=horario.hora_inicio,
        hora_fin=horario.hora_fin,
        anio_academico=horario.anio_academico,
        activo=horario.activo,
        curso_nombre=horario.curso.nombre,
        profesor_nombre=_nombre_profesor(horario.profesor) or "",
        asignatura_nombre=horario.asignatura.nombre,
        asignatura_codigo=horario.asignatura.codigo,
    )


def _horarios_overlap(inicio: time, fin: time, otro_inicio: time, otro_fin: time) -> bool:
    return inicio < otro_fin and fin > otro_inicio


def _validate_horario_conflict(
    db: Session,
    curso_id: int,
    profesor_id: int,
    dia_semana: int,
    hora_inicio: time,
    hora_fin: time,
    anio_academico: int,
    exclude_id: int | None = None,
) -> None:
    query = db.query(HorarioClase).filter(
        HorarioClase.activo.is_(True),
        HorarioClase.anio_academico == anio_academico,
        HorarioClase.dia_semana == dia_semana,
        or_(HorarioClase.profesor_id == profesor_id, HorarioClase.curso_id == curso_id),
    )
    if exclude_id:
        query = query.filter(HorarioClase.id != exclude_id)

    for horario in query.all():
        if not _horarios_overlap(hora_inicio, hora_fin, horario.hora_inicio, horario.hora_fin):
            continue
        if horario.profesor_id == profesor_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Choque de horario: el profesor ya tiene una clase en ese rango.",
            )
        if horario.curso_id == curso_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Choque de horario: el curso ya tiene una clase en ese rango.",
            )


def list_horarios(
    db: Session,
    anio_academico: int | None = None,
    curso_id: int | None = None,
    profesor_id: int | None = None,
    asignatura_id: int | None = None,
    activo: bool | None = None,
) -> list[HorarioClaseRead]:
    query = db.query(HorarioClase).options(
        joinedload(HorarioClase.curso),
        joinedload(HorarioClase.profesor),
        joinedload(HorarioClase.asignatura),
    )
    if anio_academico:
        query = query.filter(HorarioClase.anio_academico == anio_academico)
    if curso_id:
        query = query.filter(HorarioClase.curso_id == curso_id)
    if profesor_id:
        query = query.filter(HorarioClase.profesor_id == profesor_id)
    if asignatura_id:
        query = query.filter(HorarioClase.asignatura_id == asignatura_id)
    if activo is not None:
        query = query.filter(HorarioClase.activo == activo)
    horarios = query.order_by(HorarioClase.dia_semana.asc(), HorarioClase.hora_inicio.asc()).all()
    return [_serialize_horario(horario) for horario in horarios]


def get_horario(db: Session, horario_id: int) -> HorarioClase:
    horario = (
        db.query(HorarioClase)
        .options(joinedload(HorarioClase.curso), joinedload(HorarioClase.profesor), joinedload(HorarioClase.asignatura))
        .filter(HorarioClase.id == horario_id)
        .first()
    )
    if not horario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Horario no encontrado.")
    return horario


def create_horario(db: Session, payload: HorarioClaseCreate) -> HorarioClaseRead:
    data = payload.model_dump()
    _validate_horas(data["hora_inicio"], data["hora_fin"])
    _ensure_curso(db, data["curso_id"])
    _ensure_profesor(db, data["profesor_id"])
    _ensure_asignatura(db, data["asignatura_id"])
    _validate_horario_conflict(
        db,
        data["curso_id"],
        data["profesor_id"],
        data["dia_semana"],
        data["hora_inicio"],
        data["hora_fin"],
        data["anio_academico"],
    )
    horario = HorarioClase(**data)
    db.add(horario)
    db.commit()
    db.refresh(horario)
    return _serialize_horario(get_horario(db, horario.id))


def update_horario(db: Session, horario_id: int, payload: HorarioClaseUpdate) -> HorarioClaseRead:
    horario = get_horario(db, horario_id)
    data = payload.model_dump(exclude_unset=True)
    next_values = {
        "curso_id": data.get("curso_id", horario.curso_id),
        "profesor_id": data.get("profesor_id", horario.profesor_id),
        "asignatura_id": data.get("asignatura_id", horario.asignatura_id),
        "dia_semana": data.get("dia_semana", horario.dia_semana),
        "hora_inicio": data.get("hora_inicio", horario.hora_inicio),
        "hora_fin": data.get("hora_fin", horario.hora_fin),
        "anio_academico": data.get("anio_academico", horario.anio_academico),
        "activo": data.get("activo", horario.activo),
    }
    _validate_horas(next_values["hora_inicio"], next_values["hora_fin"])
    if "curso_id" in data:
        _ensure_curso(db, next_values["curso_id"])
    if "profesor_id" in data:
        _ensure_profesor(db, next_values["profesor_id"])
    if "asignatura_id" in data:
        _ensure_asignatura(db, next_values["asignatura_id"])
    if next_values["activo"]:
        _validate_horario_conflict(
            db,
            next_values["curso_id"],
            next_values["profesor_id"],
            next_values["dia_semana"],
            next_values["hora_inicio"],
            next_values["hora_fin"],
            next_values["anio_academico"],
            exclude_id=horario_id,
        )
    for field, value in data.items():
        setattr(horario, field, value)
    db.commit()
    db.refresh(horario)
    return _serialize_horario(get_horario(db, horario.id))


def delete_horario(db: Session, horario_id: int) -> None:
    horario = get_horario(db, horario_id)
    db.delete(horario)
    db.commit()


def _item_from_evento(evento: EventoAcademico) -> CalendarioItem:
    return CalendarioItem(
        id=f"evento-{evento.id}",
        source="evento",
        source_id=evento.id,
        titulo=evento.titulo,
        tipo=evento.tipo,
        fecha_inicio=evento.fecha_inicio,
        fecha_fin=evento.fecha_fin,
        curso_id=evento.curso_id,
        curso_nombre=evento.curso.nombre if evento.curso else None,
        profesor_id=evento.profesor_id,
        profesor_nombre=_nombre_profesor(evento.profesor),
        asignatura_id=evento.asignatura_id,
        asignatura_nombre=evento.asignatura.nombre if evento.asignatura else None,
        asignatura_codigo=evento.asignatura.codigo if evento.asignatura else None,
        estado=evento.estado,
    )


def _item_from_horario(horario: HorarioClase, fecha: date) -> CalendarioItem:
    fecha_inicio = datetime.combine(fecha, horario.hora_inicio)
    fecha_fin = datetime.combine(fecha, horario.hora_fin)
    return CalendarioItem(
        id=f"horario-{horario.id}-{fecha.isoformat()}",
        source="horario",
        source_id=horario.id,
        titulo=f"{horario.asignatura.nombre} - {horario.curso.nombre}",
        tipo="clase",
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        curso_id=horario.curso_id,
        curso_nombre=horario.curso.nombre,
        profesor_id=horario.profesor_id,
        profesor_nombre=_nombre_profesor(horario.profesor),
        asignatura_id=horario.asignatura_id,
        asignatura_nombre=horario.asignatura.nombre,
        asignatura_codigo=horario.asignatura.codigo,
        estado="activo" if horario.activo else "inactivo",
    )


def get_calendario_mes(
    db: Session,
    anio: int = 2026,
    mes: int = 6,
    tipo: str | None = None,
    curso_id: int | None = None,
    profesor_id: int | None = None,
    asignatura_id: int | None = None,
) -> CalendarioMesRead:
    if mes < 1 or mes > 12:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El mes debe estar entre 1 y 12.")

    last_day = monthrange(anio, mes)[1]
    start = datetime(anio, mes, 1)
    end = datetime(anio, mes, last_day, 23, 59, 59)
    items: list[CalendarioItem] = []

    if tipo != "clase":
        eventos_query = db.query(EventoAcademico).options(
            joinedload(EventoAcademico.curso),
            joinedload(EventoAcademico.profesor),
            joinedload(EventoAcademico.asignatura),
        )
        eventos_query = eventos_query.filter(
            EventoAcademico.anio_academico == anio,
            EventoAcademico.fecha_inicio <= end,
            or_(EventoAcademico.fecha_fin.is_(None), EventoAcademico.fecha_fin >= start),
            EventoAcademico.estado == "activo",
        )
        if tipo:
            eventos_query = eventos_query.filter(EventoAcademico.tipo == tipo)
        if curso_id:
            eventos_query = eventos_query.filter(EventoAcademico.curso_id == curso_id)
        if profesor_id:
            eventos_query = eventos_query.filter(EventoAcademico.profesor_id == profesor_id)
        if asignatura_id:
            eventos_query = eventos_query.filter(EventoAcademico.asignatura_id == asignatura_id)
        items.extend(_item_from_evento(evento) for evento in eventos_query.all())

    if not tipo or tipo == "clase":
        horarios_query = db.query(HorarioClase).options(
            joinedload(HorarioClase.curso),
            joinedload(HorarioClase.profesor),
            joinedload(HorarioClase.asignatura),
        )
        horarios_query = horarios_query.filter(HorarioClase.anio_academico == anio, HorarioClase.activo.is_(True))
        if curso_id:
            horarios_query = horarios_query.filter(HorarioClase.curso_id == curso_id)
        if profesor_id:
            horarios_query = horarios_query.filter(HorarioClase.profesor_id == profesor_id)
        if asignatura_id:
            horarios_query = horarios_query.filter(HorarioClase.asignatura_id == asignatura_id)
        horarios = horarios_query.all()
        current = date(anio, mes, 1)
        month_end = date(anio, mes, last_day)
        while current <= month_end:
            for horario in horarios:
                if current.isoweekday() == horario.dia_semana:
                    items.append(_item_from_horario(horario, current))
            current += timedelta(days=1)

    items.sort(key=lambda item: (item.fecha_inicio, item.titulo))
    return CalendarioMesRead(anio=anio, mes=mes, items=items)


def get_proximos_eventos(db: Session, limit: int = 5) -> list[CalendarioItem]:
    limit = max(1, min(limit, 50))
    today = date.today()
    items: list[CalendarioItem] = []

    eventos = (
        db.query(EventoAcademico)
        .options(joinedload(EventoAcademico.curso), joinedload(EventoAcademico.profesor), joinedload(EventoAcademico.asignatura))
        .filter(EventoAcademico.fecha_inicio >= datetime.combine(today, time.min), EventoAcademico.estado == "activo")
        .order_by(EventoAcademico.fecha_inicio.asc())
        .limit(limit)
        .all()
    )
    items.extend(_item_from_evento(evento) for evento in eventos)

    horarios = (
        db.query(HorarioClase)
        .options(joinedload(HorarioClase.curso), joinedload(HorarioClase.profesor), joinedload(HorarioClase.asignatura))
        .filter(HorarioClase.activo.is_(True))
        .all()
    )
    current = today
    horizon = today + timedelta(days=45)
    while current <= horizon and len(items) < limit * 4:
        for horario in horarios:
            if current.isoweekday() == horario.dia_semana:
                items.append(_item_from_horario(horario, current))
        current += timedelta(days=1)

    items.sort(key=lambda item: (item.fecha_inicio, item.titulo))
    return items[:limit]
