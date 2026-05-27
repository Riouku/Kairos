from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers import dashboard_controller
from app.database import get_db
from app.schemas import DashboardResumen

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/resumen", response_model=DashboardResumen)
def get_resumen(db: Session = Depends(get_db)):
    return dashboard_controller.get_resumen(db)
