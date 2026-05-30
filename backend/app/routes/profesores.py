from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.controllers import profesores_controller
from app.database import get_db
from app.schemas import ProfesorCreate, ProfesorRead, ProfesorUpdate

router = APIRouter(prefix="/profesores", tags=["Profesores"])


@router.get("", response_model=list[ProfesorRead])
def list_profesores(
    search: str | None = None,
    activo: bool | None = None,
    db: Session = Depends(get_db),
):
    return profesores_controller.list_profesores(db, search, activo)


@router.get("/{profesor_id}", response_model=ProfesorRead)
def get_profesor(profesor_id: int, db: Session = Depends(get_db)):
    return profesores_controller.get_profesor(db, profesor_id)


@router.post("", response_model=ProfesorRead, status_code=status.HTTP_201_CREATED)
def create_profesor(payload: ProfesorCreate, db: Session = Depends(get_db)):
    return profesores_controller.create_profesor(db, payload)


@router.put("/{profesor_id}", response_model=ProfesorRead)
def update_profesor(profesor_id: int, payload: ProfesorUpdate, db: Session = Depends(get_db)):
    return profesores_controller.update_profesor(db, profesor_id, payload)


@router.patch("/{profesor_id}/estado", response_model=ProfesorRead)
def update_profesor_estado(profesor_id: int, activo: bool, db: Session = Depends(get_db)):
    return profesores_controller.update_profesor_estado(db, profesor_id, activo)


@router.delete("/{profesor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_profesor(profesor_id: int, db: Session = Depends(get_db)):
    profesores_controller.delete_profesor(db, profesor_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
