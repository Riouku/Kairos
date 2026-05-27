from sqlalchemy.orm import Session, joinedload

from app.controllers.asignaciones_controller import serialize_asignacion
from app.models import Asignacion, Asignatura, Profesor
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
        asignaciones_mes_destacado=actuales_por_mes[mes_mas_activo_numero] if asignaciones else 0,
        mes_mas_activo=mes_mas_activo,
        estadisticas_mensuales=estadisticas_mensuales,
        ultimas_asignaciones=[serialize_asignacion(asignacion) for asignacion in ultimas],
    )
