from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.controllers import notas_controller
from app.database import get_db
from app.schemas import NotaCreate, NotaRead, NotaResumenRead, NotaUpdate

router = APIRouter(prefix="/notas", tags=["Notas"])


@router.get("/resumen", response_model=NotaResumenRead)
def get_notas_resumen(
    curso_id: int | None = None,
    asignatura_id: int | None = None,
    estudiante_id: int | None = None,
    periodo_id: int | None = None,
    anio_academico: int | None = None,
    db: Session = Depends(get_db),
):
    return notas_controller.get_notas_resumen(db, curso_id, asignatura_id, estudiante_id, periodo_id, anio_academico)


@router.get("", response_model=list[NotaRead])
def list_notas(
    estudiante_id: int | None = None,
    evaluacion_id: int | None = None,
    curso_id: int | None = None,
    asignatura_id: int | None = None,
    profesor_id: int | None = None,
    periodo_id: int | None = None,
    anio_academico: int | None = None,
    db: Session = Depends(get_db),
):
    return notas_controller.list_notas(db, estudiante_id, evaluacion_id, curso_id, asignatura_id, profesor_id, periodo_id, anio_academico)


@router.post("", response_model=NotaRead, status_code=status.HTTP_201_CREATED)
def create_or_update_nota(payload: NotaCreate, db: Session = Depends(get_db)):
    return notas_controller.create_or_update_nota(db, payload)


@router.put("/{nota_id}", response_model=NotaRead)
def update_nota(nota_id: int, payload: NotaUpdate, db: Session = Depends(get_db)):
    return notas_controller.update_nota(db, nota_id, payload)


@router.delete("/{nota_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_nota(nota_id: int, db: Session = Depends(get_db)):
    notas_controller.delete_nota(db, nota_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
