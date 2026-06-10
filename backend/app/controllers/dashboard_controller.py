from datetime import date

from sqlalchemy.orm import Session, joinedload

from app.controllers.asignaciones_controller import serialize_asignacion
from app.controllers.asistencia_controller import get_asistencia_resumen
from app.controllers.notas_controller import get_notas_resumen, serialize_nota
from app.models import Asignacion, Asignatura, Asistencia, Estudiante, Evaluacion, Nota, Profesor
from app.schemas import DashboardResumen, EstadisticaMensual


MESES = [
    "Ene",
    "Feb",
    "Mar",
    "Abr",
    "May",
    "Jun",
    "Jul",
    "Ago",
    "Sep",
    "Oct",
    "Nov",
    "Dic",
]


def get_resumen(db: Session) -> DashboardResumen:
    ultimas = (
        db.query(Asignacion)
        .options(joinedload(Asignacion.profesor), joinedload(Asignacion.asignatura))
        .order_by(Asignacion.fecha_asignacion.desc(), Asignacion.id.desc())
        .limit(5)
        .all()
    )
    asignaciones = db.query(Asignacion.fecha_asignacion).all()
    ultimas_notas = (
        db.query(Nota)
        .options(
            joinedload(Nota.estudiante),
            joinedload(Nota.evaluacion).joinedload(Evaluacion.curso),
            joinedload(Nota.evaluacion).joinedload(Evaluacion.asignatura),
            joinedload(Nota.evaluacion).joinedload(Evaluacion.profesor),
            joinedload(Nota.evaluacion).joinedload(Evaluacion.periodo),
        )
        .order_by(Nota.fecha_registro.desc(), Nota.id.desc())
        .limit(5)
        .all()
    )
    resumen_notas = get_notas_resumen(db)
    hoy = date.today()
    resumen_asistencia = get_asistencia_resumen(db, None, hoy.month, hoy.year)
    actuales_por_mes = {mes: 0 for mes in range(1, 13)}
    for (fecha_asignacion,) in asignaciones:
        actuales_por_mes[fecha_asignacion.month] += 1

    estadisticas_mensuales = [
        EstadisticaMensual(mes=MESES[mes - 1], total=actuales_por_mes[mes])
        for mes in range(1, 13)
    ]
    mes_mas_activo_numero = max(actuales_por_mes, key=actuales_por_mes.get)
    mes_mas_activo = MESES[mes_mas_activo_numero - 1] if actuales_por_mes[mes_mas_activo_numero] else "Sin datos"

    return DashboardResumen(
        total_profesores=db.query(Profesor).count(),
        total_asignaturas=db.query(Asignatura).count(),
        total_asignaciones=db.query(Asignacion).count(),
        total_estudiantes=db.query(Estudiante).count(),
        total_evaluaciones=db.query(Evaluacion).filter(Evaluacion.estado == "activa").count(),
        total_notas=db.query(Nota).count(),
        total_asistencias=db.query(Asistencia).count(),
        promedio_general=resumen_notas.promedio_general,
        porcentaje_asistencia=resumen_asistencia.porcentaje_asistencia,
        asignaciones_mes_destacado=actuales_por_mes[mes_mas_activo_numero] if asignaciones else 0,
        mes_mas_activo=mes_mas_activo,
        estadisticas_mensuales=estadisticas_mensuales,
        ultimas_asignaciones=[serialize_asignacion(asignacion) for asignacion in ultimas],
        ultimas_notas=[serialize_nota(nota) for nota in ultimas_notas],
    )
