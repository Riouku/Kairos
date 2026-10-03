from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Asistencia, Evaluacion, EventoAcademico, RetiroEstudiante
from app.models.apoderado import Apoderado, VinculoApoderado
from app.models.estudiante import Estudiante

router = APIRouter(prefix="/apoderados", tags=["Apoderados y avisos"])


class ApoderadoInput(BaseModel):
    rut: str | None = Field(default=None, max_length=12)
    nombre: str = Field(min_length=1, max_length=100)
    apellido: str = Field(min_length=1, max_length=100)
    correo: str | None = Field(default=None, max_length=150)
    telefono: str | None = Field(default=None, max_length=30)
    activo: bool = True
    estudiante_ids: list[int] = Field(default_factory=list, max_length=30)
    parentesco: str | None = Field(default=None, max_length=50)
    recibe_avisos: bool = True

    @field_validator("rut", "nombre", "apellido", "correo", "telefono", "parentesco", mode="before")
    @classmethod
    def trim_strings(cls, value):
        if isinstance(value, str):
            return value.strip() or None
        return value


def _serialize(apoderado: Apoderado) -> dict:
    vinculos = sorted(apoderado.vinculos, key=lambda item: (item.estudiante.apellido, item.estudiante.nombre))
    return {
        "id": apoderado.id,
        "rut": apoderado.rut,
        "nombre": apoderado.nombre,
        "apellido": apoderado.apellido,
        "correo": apoderado.correo,
        "telefono": apoderado.telefono,
        "activo": apoderado.activo,
        "estudiantes": [{
            "id": link.estudiante.id,
            "nombre": f"{link.estudiante.nombre} {link.estudiante.apellido}",
            "curso": link.estudiante.curso.nombre if link.estudiante.curso else "Sin curso",
            "parentesco": link.parentesco,
            "recibe_avisos": link.recibe_avisos,
        } for link in vinculos],
    }


def _get_apoderado(db: Session, apoderado_id: int) -> Apoderado:
    item = db.query(Apoderado).options(
        joinedload(Apoderado.vinculos).joinedload(VinculoApoderado.estudiante).joinedload(Estudiante.curso)
    ).filter(Apoderado.id == apoderado_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Apoderado no encontrado.")
    return item


def _apply_students(db: Session, apoderado: Apoderado, payload: ApoderadoInput) -> None:
    student_ids = list(dict.fromkeys(payload.estudiante_ids))
    students = db.query(Estudiante).filter(Estudiante.id.in_(student_ids)).all() if student_ids else []
    if len(students) != len(student_ids):
        raise HTTPException(status_code=422, detail="Uno o más estudiantes seleccionados no existen.")
    current = {link.estudiante_id: link for link in apoderado.vinculos}
    selected = set(student_ids)
    for student_id in current.keys() - selected:
        db.delete(current[student_id])
    for student_id in selected:
        if student_id in current:
            current[student_id].parentesco = payload.parentesco
            current[student_id].recibe_avisos = payload.recibe_avisos
        else:
            apoderado.vinculos.append(VinculoApoderado(
                estudiante_id=student_id,
                parentesco=payload.parentesco,
                recibe_avisos=payload.recibe_avisos,
            ))


@router.get("")
def listar_apoderados(db: Session = Depends(get_db)):
    items = db.query(Apoderado).options(
        joinedload(Apoderado.vinculos).joinedload(VinculoApoderado.estudiante).joinedload(Estudiante.curso)
    ).order_by(Apoderado.apellido, Apoderado.nombre).all()
    return [_serialize(item) for item in items]


@router.get("/{apoderado_id}")
def detalle_apoderado(apoderado_id: int, db: Session = Depends(get_db)):
    return _serialize(_get_apoderado(db, apoderado_id))


@router.post("", status_code=status.HTTP_201_CREATED)
def crear_apoderado(payload: ApoderadoInput, db: Session = Depends(get_db)):
    data = payload.model_dump(exclude={"estudiante_ids", "parentesco", "recibe_avisos"})
    data["correo"] = data["correo"].lower() if data["correo"] else None
    item = Apoderado(**data)
    _apply_students(db, item, payload)
    db.add(item)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return _serialize(_get_apoderado(db, item.id))


@router.put("/{apoderado_id}")
def actualizar_apoderado(apoderado_id: int, payload: ApoderadoInput, db: Session = Depends(get_db)):
    item = _get_apoderado(db, apoderado_id)
    data = payload.model_dump(exclude={"estudiante_ids", "parentesco", "recibe_avisos"})
    data["correo"] = data["correo"].lower() if data["correo"] else None
    for key, value in data.items():
        setattr(item, key, value)
    _apply_students(db, item, payload)
    db.commit()
    return _serialize(_get_apoderado(db, item.id))


@router.delete("/{apoderado_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_apoderado(apoderado_id: int, db: Session = Depends(get_db)):
    item = _get_apoderado(db, apoderado_id)
    db.delete(item)
    db.commit()


@router.get("/{apoderado_id}/avisos")
def avisos_apoderado(apoderado_id: int, db: Session = Depends(get_db)):
    apoderado = _get_apoderado(db, apoderado_id)
    student_ids = [link.estudiante_id for link in apoderado.vinculos if link.recibe_avisos]
    if not student_ids:
        return []
    student_by_id = {link.estudiante_id: link.estudiante for link in apoderado.vinculos if link.recibe_avisos}
    student_courses = {student.curso_id for student in student_by_id.values()}
    today = date.today()
    since = today - timedelta(days=45)
    until = today + timedelta(days=60)
    notices: list[dict] = []

    def student_label(student_id: int) -> str:
        student = student_by_id[student_id]
        return f"{student.nombre} {student.apellido}"

    events = db.query(EventoAcademico).filter(
        EventoAcademico.estado == "activo",
        EventoAcademico.fecha_inicio >= datetime.combine(since, time.min),
        EventoAcademico.fecha_inicio < datetime.combine(until + timedelta(days=1), time.min),
        (EventoAcademico.curso_id.in_(student_courses) | EventoAcademico.curso_id.is_(None)),
    ).order_by(EventoAcademico.fecha_inicio).all() if student_courses else []
    for event in events:
        recipients = [student_id for student_id in student_ids if event.curso_id is None or student_by_id[student_id].curso_id == event.curso_id]
        for student_id in recipients:
            notices.append({"tipo": "Evento", "fecha": event.fecha_inicio, "estudiante": student_label(student_id),
                            "titulo": event.titulo, "detalle": event.descripcion or event.tipo})

    evaluations = db.query(Evaluacion).options(joinedload(Evaluacion.asignatura)).filter(
        Evaluacion.estado == "activa", Evaluacion.curso_id.in_(student_courses),
        Evaluacion.fecha >= since, Evaluacion.fecha <= until,
    ).order_by(Evaluacion.fecha).all() if student_courses else []
    for evaluation in evaluations:
        for student_id in student_ids:
            if student_by_id[student_id].curso_id == evaluation.curso_id:
                subject = evaluation.asignatura.nombre if evaluation.asignatura else ""
                notices.append({"tipo": "Evaluación", "fecha": evaluation.fecha, "estudiante": student_label(student_id),
                                "titulo": evaluation.titulo, "detalle": subject})

    attendance = db.query(Asistencia).filter(
        Asistencia.estudiante_id.in_(student_ids), Asistencia.fecha >= since,
        Asistencia.estado.in_(["ausente", "justificado"]),
    ).order_by(Asistencia.fecha.desc()).limit(150).all()
    for record in attendance:
        notices.append({"tipo": "Asistencia", "fecha": record.fecha, "estudiante": student_label(record.estudiante_id),
                        "titulo": "Ausencia registrada" if record.estado == "ausente" else "Inasistencia justificada",
                        "detalle": record.observacion or record.estado.capitalize()})

    retirements = db.query(RetiroEstudiante).filter(
        RetiroEstudiante.estudiante_id.in_(student_ids),
        RetiroEstudiante.fecha_hora >= datetime.combine(since, time.min),
    ).order_by(RetiroEstudiante.fecha_hora.desc()).limit(100).all()
    for record in retirements:
        notices.append({"tipo": "Retiro", "fecha": record.fecha_hora, "estudiante": student_label(record.estudiante_id),
                        "titulo": f"Retiro autorizado por {record.autorizado_por}",
                        "detalle": f"Retiró {record.retirado_por}" + (f" · {record.motivo}" if record.motivo else "")})

    return sorted(notices, key=lambda notice: str(notice["fecha"]), reverse=True)
