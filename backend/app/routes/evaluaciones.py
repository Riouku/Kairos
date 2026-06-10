from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.controllers import notas_controller
from app.database import get_db
from app.schemas import EvaluacionCreate, EvaluacionRead, EvaluacionUpdate

router = APIRouter(prefix="/evaluaciones", tags=["Evaluaciones"])


@router.get("", response_model=list[EvaluacionRead])
def list_evaluaciones(
    anio_academico: int | None = None,
    curso_id: int | None = None,
    profesor_id: int | None = None,
    asignatura_id: int | None = None,
    periodo_id: int | None = None,
    estado: str | None = None,
    db: Session = Depends(get_db),
):
    return notas_controller.list_evaluaciones(db, anio_academico, curso_id, profesor_id, asignatura_id, periodo_id, estado)


@router.get("/{evaluacion_id}", response_model=EvaluacionRead)
def get_evaluacion(evaluacion_id: int, db: Session = Depends(get_db)):
    return notas_controller.get_evaluacion_read(db, evaluacion_id)


@router.post("", response_model=EvaluacionRead, status_code=status.HTTP_201_CREATED)
def create_evaluacion(payload: EvaluacionCreate, db: Session = Depends(get_db)):
    return notas_controller.create_evaluacion(db, payload)


@router.put("/{evaluacion_id}", response_model=EvaluacionRead)
def update_evaluacion(evaluacion_id: int, payload: EvaluacionUpdate, db: Session = Depends(get_db)):
    return notas_controller.update_evaluacion(db, evaluacion_id, payload)


@router.patch("/{evaluacion_id}/estado", response_model=EvaluacionRead)
def update_evaluacion_estado(evaluacion_id: int, estado_evaluacion: str, db: Session = Depends(get_db)):
    return notas_controller.update_evaluacion_estado(db, evaluacion_id, estado_evaluacion)


@router.delete("/{evaluacion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_evaluacion(evaluacion_id: int, db: Session = Depends(get_db)):
    notas_controller.delete_evaluacion(db, evaluacion_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
