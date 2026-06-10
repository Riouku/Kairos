from datetime import date

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.controllers import asistencia_controller
from app.database import get_db
from app.schemas import (
    AsistenciaBulkCreate,
    AsistenciaCreate,
    AsistenciaRead,
    AsistenciaResumenRead,
    AsistenciaUpdate,
)

router = APIRouter(prefix="/asistencias", tags=["Asistencias"])


@router.get("/resumen", response_model=AsistenciaResumenRead)
def get_asistencia_resumen(
    curso_id: int | None = None,
    mes: int = 6,
    anio_academico: int = 2026,
    db: Session = Depends(get_db),
):
    return asistencia_controller.get_asistencia_resumen(db, curso_id, mes, anio_academico)


@router.get("", response_model=list[AsistenciaRead])
def list_asistencias(
    curso_id: int | None = None,
    estudiante_id: int | None = None,
    fecha: date | None = None,
    mes: int | None = None,
    anio_academico: int | None = None,
    db: Session = Depends(get_db),
):
    return asistencia_controller.list_asistencias(db, curso_id, estudiante_id, fecha, mes, anio_academico)


@router.post("", response_model=AsistenciaRead, status_code=status.HTTP_201_CREATED)
def create_or_update_asistencia(payload: AsistenciaCreate, db: Session = Depends(get_db)):
    return asistencia_controller.create_or_update_asistencia(db, payload)


@router.post("/bulk", response_model=list[AsistenciaRead], status_code=status.HTTP_201_CREATED)
def create_or_update_asistencias_bulk(payload: AsistenciaBulkCreate, db: Session = Depends(get_db)):
    return asistencia_controller.create_or_update_asistencias_bulk(db, payload)


@router.put("/{asistencia_id}", response_model=AsistenciaRead)
def update_asistencia(asistencia_id: int, payload: AsistenciaUpdate, db: Session = Depends(get_db)):
    return asistencia_controller.update_asistencia(db, asistencia_id, payload)


@router.delete("/{asistencia_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asistencia(asistencia_id: int, db: Session = Depends(get_db)):
    asistencia_controller.delete_asistencia(db, asistencia_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
