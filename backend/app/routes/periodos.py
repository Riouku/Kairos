from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.controllers import notas_controller
from app.database import get_db
from app.schemas import PeriodoAcademicoCreate, PeriodoAcademicoRead, PeriodoAcademicoUpdate

router = APIRouter(prefix="/periodos", tags=["Periodos academicos"])


@router.get("", response_model=list[PeriodoAcademicoRead])
def list_periodos(
    activo: bool | None = None,
    anio_academico: int | None = None,
    db: Session = Depends(get_db),
):
    return notas_controller.list_periodos(db, activo, anio_academico)


@router.get("/{periodo_id}", response_model=PeriodoAcademicoRead)
def get_periodo(periodo_id: int, db: Session = Depends(get_db)):
    return notas_controller.get_periodo(db, periodo_id)


@router.post("", response_model=PeriodoAcademicoRead, status_code=status.HTTP_201_CREATED)
def create_periodo(payload: PeriodoAcademicoCreate, db: Session = Depends(get_db)):
    return notas_controller.create_periodo(db, payload)


@router.put("/{periodo_id}", response_model=PeriodoAcademicoRead)
def update_periodo(periodo_id: int, payload: PeriodoAcademicoUpdate, db: Session = Depends(get_db)):
    return notas_controller.update_periodo(db, periodo_id, payload)


@router.delete("/{periodo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_periodo(periodo_id: int, db: Session = Depends(get_db)):
    notas_controller.delete_periodo(db, periodo_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
