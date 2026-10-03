from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Asistencia, Curso, Estudiante, Evaluacion, Nota
from app.models.biblioteca import Libro, PrestamoLibro

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/asistencia")
def reporte_asistencia(desde: date | None = None, hasta: date | None = None,
                       curso_id: int | None = None, db: Session = Depends(get_db)):
    hasta = hasta or date.today()
    desde = desde or date(hasta.year, 1, 1)
    query = db.query(Asistencia).options(
        joinedload(Asistencia.estudiante), joinedload(Asistencia.curso)
    ).filter(Asistencia.fecha >= desde, Asistencia.fecha <= hasta)
    if curso_id:
        query = query.filter(Asistencia.curso_id == curso_id)
    grouped: dict[tuple[int, int], dict] = {}
    for item in query.order_by(Asistencia.estudiante_id, Asistencia.fecha).all():
        key = (item.estudiante_id, item.curso_id)
        row = grouped.setdefault(key, {
            "estudiante_id": item.estudiante_id,
            "estudiante": f"{item.estudiante.nombre} {item.estudiante.apellido}",
            "rut": item.estudiante.rut,
            "curso": item.curso.nombre if item.curso else "Sin curso",
            "registros": 0,
            "presentes": 0,
            "ausentes": 0,
            "justificados": 0,
            "porcentaje_asistencia": 0,
        })
        row["registros"] += 1
        if item.estado == "presente":
            row["presentes"] += 1
        elif item.estado == "ausente":
            row["ausentes"] += 1
        elif item.estado == "justificado":
            row["justificados"] += 1
    for row in grouped.values():
        row["porcentaje_asistencia"] = round(row["presentes"] * 100 / row["registros"], 1) if row["registros"] else 0
    return {"desde": desde, "hasta": hasta, "resultados": list(grouped.values())}


@router.get("/promedios")
def reporte_promedios(anio_academico: int | None = None, curso_id: int | None = None,
                      desde: date | None = None, hasta: date | None = None,
                      db: Session = Depends(get_db)):
    query = db.query(Nota).join(Evaluacion).options(
        joinedload(Nota.estudiante), joinedload(Nota.evaluacion).joinedload(Evaluacion.curso)
    ).filter(Evaluacion.estado == "activa")
    if anio_academico:
        query = query.filter(Evaluacion.anio_academico == anio_academico)
    if curso_id:
        query = query.filter(Evaluacion.curso_id == curso_id)
    if desde:
        query = query.filter(Evaluacion.fecha >= desde)
    if hasta:
        query = query.filter(Evaluacion.fecha <= hasta)
    grouped: dict[tuple[int, int], dict] = {}
    for item in query.all():
        key = (item.estudiante_id, item.evaluacion.curso_id)
        row = grouped.setdefault(key, {
            "estudiante_id": item.estudiante_id,
            "estudiante": f"{item.estudiante.nombre} {item.estudiante.apellido}",
            "rut": item.estudiante.rut,
            "curso": item.evaluacion.curso.nombre if item.evaluacion.curso else "Sin curso",
            "suma_ponderada": 0.0,
            "ponderacion_total": 0.0,
            "evaluaciones": 0,
        })
        weight = float(item.evaluacion.ponderacion or 1)
        row["suma_ponderada"] += float(item.nota) * weight
        row["ponderacion_total"] += weight
        row["evaluaciones"] += 1
    results = []
    for row in grouped.values():
        row["promedio"] = round(row["suma_ponderada"] / row["ponderacion_total"], 2) if row["ponderacion_total"] else None
        del row["suma_ponderada"]
        del row["ponderacion_total"]
        results.append(row)
    return sorted(results, key=lambda row: (row["curso"], row["estudiante"]))


@router.get("/matriculas")
def reporte_matriculas(anio_academico: int | None = None, curso_id: int | None = None,
                       db: Session = Depends(get_db)):
    query = db.query(Estudiante).options(joinedload(Estudiante.curso))
    if anio_academico:
        query = query.filter(Estudiante.anio_academico == anio_academico)
    if curso_id:
        query = query.filter(Estudiante.curso_id == curso_id)
    return [{"estudiante_id": item.id, "rut": item.rut,
             "estudiante": f"{item.nombre} {item.apellido}",
             "curso": item.curso.nombre if item.curso else "Sin curso",
             "anio_academico": item.anio_academico,
             "estado": "Activo" if item.activo else "Inactivo"}
            for item in query.order_by(Estudiante.anio_academico.desc(), Estudiante.apellido, Estudiante.nombre).all()]


@router.get("/prestamos-vencidos")
def reporte_prestamos_vencidos(curso_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(PrestamoLibro).options(
        joinedload(PrestamoLibro.libro), joinedload(PrestamoLibro.estudiante).joinedload(Estudiante.curso)
    ).filter(PrestamoLibro.devuelto_en.is_(None), PrestamoLibro.fecha_devolucion < date.today())
    if curso_id:
        query = query.join(Estudiante, PrestamoLibro.estudiante_id == Estudiante.id).filter(Estudiante.curso_id == curso_id)
    return [{"prestamo_id": item.id, "estudiante": f"{item.estudiante.nombre} {item.estudiante.apellido}",
             "curso": item.estudiante.curso.nombre if item.estudiante.curso else "Sin curso",
             "libro": item.libro.titulo, "fecha_prestamo": item.fecha_prestamo,
             "fecha_devolucion": item.fecha_devolucion,
             "dias_atraso": (date.today() - item.fecha_devolucion).days}
            for item in query.order_by(PrestamoLibro.fecha_devolucion).all()]
