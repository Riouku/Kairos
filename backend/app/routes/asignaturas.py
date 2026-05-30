from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.controllers import asignaturas_controller
from app.database import get_db
from app.schemas import AsignaturaCreate, AsignaturaRead, AsignaturaUpdate

router = APIRouter(prefix="/asignaturas", tags=["Asignaturas"])


@router.get("", response_model=list[AsignaturaRead])
def list_asignaturas(
    search: str | None = None,
    activo: bool | None = None,
    nivel: str | None = None,
    db: Session = Depends(get_db),
):
    return asignaturas_controller.list_asignaturas(db, search, activo, nivel)


@router.get("/{asignatura_id}", response_model=AsignaturaRead)
def get_asignatura(asignatura_id: int, db: Session = Depends(get_db)):
    return asignaturas_controller.get_asignatura(db, asignatura_id)


@router.post("", response_model=AsignaturaRead, status_code=status.HTTP_201_CREATED)
def create_asignatura(payload: AsignaturaCreate, db: Session = Depends(get_db)):
    return asignaturas_controller.create_asignatura(db, payload)


@router.put("/{asignatura_id}", response_model=AsignaturaRead)
def update_asignatura(asignatura_id: int, payload: AsignaturaUpdate, db: Session = Depends(get_db)):
    return asignaturas_controller.update_asignatura(db, asignatura_id, payload)


@router.patch("/{asignatura_id}/estado", response_model=AsignaturaRead)
def update_asignatura_estado(asignatura_id: int, activo: bool, db: Session = Depends(get_db)):
    return asignaturas_controller.update_asignatura_estado(db, asignatura_id, activo)


@router.delete("/{asignatura_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asignatura(asignatura_id: int, db: Session = Depends(get_db)):
    asignaturas_controller.delete_asignatura(db, asignatura_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
