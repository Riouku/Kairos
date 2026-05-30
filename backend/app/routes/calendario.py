from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.controllers import calendario_controller
from app.database import get_db
from app.schemas import (
    CalendarioItem,
    CalendarioMesRead,
    EventoAcademicoCreate,
    EventoAcademicoRead,
    EventoAcademicoUpdate,
    HorarioClaseCreate,
    HorarioClaseRead,
    HorarioClaseUpdate,
)

router = APIRouter(prefix="/calendario", tags=["Calendario"])


@router.get("", response_model=CalendarioMesRead)
def get_calendario_mes(
    anio: int = 2026,
    mes: int = 6,
    tipo: str | None = None,
    curso_id: int | None = None,
    profesor_id: int | None = None,
    asignatura_id: int | None = None,
    db: Session = Depends(get_db),
):
    return calendario_controller.get_calendario_mes(db, anio, mes, tipo, curso_id, profesor_id, asignatura_id)


@router.get("/proximos", response_model=list[CalendarioItem])
def get_proximos_eventos(limit: int = 5, db: Session = Depends(get_db)):
    return calendario_controller.get_proximos_eventos(db, limit)


@router.get("/eventos", response_model=list[EventoAcademicoRead])
def list_eventos(
    anio_academico: int | None = None,
    tipo: str | None = None,
    curso_id: int | None = None,
    profesor_id: int | None = None,
    asignatura_id: int | None = None,
    db: Session = Depends(get_db),
):
    return calendario_controller.list_eventos(db, anio_academico, tipo, curso_id, profesor_id, asignatura_id)


@router.post("/eventos", response_model=EventoAcademicoRead, status_code=status.HTTP_201_CREATED)
def create_evento(payload: EventoAcademicoCreate, db: Session = Depends(get_db)):
    return calendario_controller.create_evento(db, payload)


@router.put("/eventos/{evento_id}", response_model=EventoAcademicoRead)
def update_evento(evento_id: int, payload: EventoAcademicoUpdate, db: Session = Depends(get_db)):
    return calendario_controller.update_evento(db, evento_id, payload)


@router.delete("/eventos/{evento_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_evento(evento_id: int, db: Session = Depends(get_db)):
    calendario_controller.delete_evento(db, evento_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/horarios", response_model=list[HorarioClaseRead])
def list_horarios(
    anio_academico: int | None = None,
    curso_id: int | None = None,
    profesor_id: int | None = None,
    asignatura_id: int | None = None,
    activo: bool | None = None,
    db: Session = Depends(get_db),
):
    return calendario_controller.list_horarios(db, anio_academico, curso_id, profesor_id, asignatura_id, activo)


@router.post("/horarios", response_model=HorarioClaseRead, status_code=status.HTTP_201_CREATED)
def create_horario(payload: HorarioClaseCreate, db: Session = Depends(get_db)):
    return calendario_controller.create_horario(db, payload)


@router.put("/horarios/{horario_id}", response_model=HorarioClaseRead)
def update_horario(horario_id: int, payload: HorarioClaseUpdate, db: Session = Depends(get_db)):
    return calendario_controller.update_horario(db, horario_id, payload)


@router.delete("/horarios/{horario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_horario(horario_id: int, db: Session = Depends(get_db)):
    calendario_controller.delete_horario(db, horario_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
