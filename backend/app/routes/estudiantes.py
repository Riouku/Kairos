from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.controllers import notas_controller
from app.database import get_db
from app.schemas import EstudianteCreate, EstudianteRead, EstudianteUpdate

router = APIRouter(prefix="/estudiantes", tags=["Estudiantes"])


@router.get("", response_model=list[EstudianteRead])
def list_estudiantes(
    search: str | None = None,
    activo: bool | None = None,
    curso_id: int | None = None,
    anio_academico: int | None = None,
    db: Session = Depends(get_db),
):
    return notas_controller.list_estudiantes(db, search, activo, curso_id, anio_academico)


@router.get("/{estudiante_id}", response_model=EstudianteRead)
def get_estudiante(estudiante_id: int, db: Session = Depends(get_db)):
    return notas_controller.get_estudiante(db, estudiante_id)


@router.post("", response_model=EstudianteRead, status_code=status.HTTP_201_CREATED)
def create_estudiante(payload: EstudianteCreate, db: Session = Depends(get_db)):
    return notas_controller.create_estudiante(db, payload)


@router.put("/{estudiante_id}", response_model=EstudianteRead)
def update_estudiante(estudiante_id: int, payload: EstudianteUpdate, db: Session = Depends(get_db)):
    return notas_controller.update_estudiante(db, estudiante_id, payload)


@router.patch("/{estudiante_id}/estado", response_model=EstudianteRead)
def update_estudiante_estado(estudiante_id: int, activo: bool, db: Session = Depends(get_db)):
    return notas_controller.update_estudiante_estado(db, estudiante_id, activo)


@router.delete("/{estudiante_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_estudiante(estudiante_id: int, db: Session = Depends(get_db)):
    notas_controller.delete_estudiante(db, estudiante_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
