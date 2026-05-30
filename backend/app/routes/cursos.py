from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.controllers import calendario_controller
from app.database import get_db
from app.schemas import CursoCreate, CursoRead, CursoUpdate

router = APIRouter(prefix="/cursos", tags=["Cursos"])


@router.get("", response_model=list[CursoRead])
def list_cursos(
    search: str | None = None,
    activo: bool | None = None,
    anio_academico: int | None = None,
    db: Session = Depends(get_db),
):
    return calendario_controller.list_cursos(db, search, activo, anio_academico)


@router.get("/{curso_id}", response_model=CursoRead)
def get_curso(curso_id: int, db: Session = Depends(get_db)):
    return calendario_controller.get_curso(db, curso_id)


@router.post("", response_model=CursoRead, status_code=status.HTTP_201_CREATED)
def create_curso(payload: CursoCreate, db: Session = Depends(get_db)):
    return calendario_controller.create_curso(db, payload)


@router.put("/{curso_id}", response_model=CursoRead)
def update_curso(curso_id: int, payload: CursoUpdate, db: Session = Depends(get_db)):
    return calendario_controller.update_curso(db, curso_id, payload)


@router.delete("/{curso_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_curso(curso_id: int, db: Session = Depends(get_db)):
    calendario_controller.delete_curso(db, curso_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
