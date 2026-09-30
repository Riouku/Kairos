from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import Estudiante
from app.models.retiro_estudiante import RetiroEstudiante
router=APIRouter(prefix="/retiros",tags=["Retiros de estudiantes"])
class RetiroIn(BaseModel):
    estudiante_id:int
    retirado_por:str=Field(min_length=2,max_length=150)
    autorizado_por:str=Field(min_length=2,max_length=150)
    motivo:str|None=None
@router.get("")
def listar(db:Session=Depends(get_db)):
    rows=db.query(RetiroEstudiante).options(joinedload(RetiroEstudiante.estudiante)).order_by(RetiroEstudiante.fecha_hora.desc()).limit(300).all()
    return [{"id":r.id,"estudiante_id":r.estudiante_id,"estudiante":r.estudiante.nombre+" "+r.estudiante.apellido,"curso":r.estudiante.curso.nombre if r.estudiante.curso else "","retirado_por":r.retirado_por,"autorizado_por":r.autorizado_por,"motivo":r.motivo,"fecha_hora":r.fecha_hora} for r in rows]
@router.post("",status_code=201)
def crear(data:RetiroIn,db:Session=Depends(get_db)):
    e=db.get(Estudiante,data.estudiante_id)
    if not e or not e.activo: raise HTTPException(404,"Estudiante activo no encontrado.")
    r=RetiroEstudiante(**data.model_dump(),fecha_hora=datetime.now()); db.add(r); db.commit(); db.refresh(r); return {"id":r.id,"fecha_hora":r.fecha_hora}
