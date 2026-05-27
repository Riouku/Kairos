from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.controllers import asignaciones_controller
from app.database import get_db
from app.schemas import AsignacionCreate, AsignacionRead

router = APIRouter(prefix="/asignaciones", tags=["Asignaciones"])


@router.get("", response_model=list[AsignacionRead])
def list_asignaciones(db: Session = Depends(get_db)):
    return asignaciones_controller.list_asignaciones(db)


@router.post("", response_model=AsignacionRead, status_code=status.HTTP_201_CREATED)
def create_asignacion(payload: AsignacionCreate, db: Session = Depends(get_db)):
    return asignaciones_controller.create_asignacion(db, payload)


@router.delete("/{asignacion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asignacion(asignacion_id: int, db: Session = Depends(get_db)):
    asignaciones_controller.delete_asignacion(db, asignacion_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
