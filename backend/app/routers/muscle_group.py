from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.muscle_group import MuscleGroup
from app.schemas.muscle_group import MuscleGroupRead

router = APIRouter(prefix="/muscle-groups", tags=["muscle groups"])

#read only..can't add muscle groups thru ui so no POST/PUT/DELETE
@router.get("/", response_model=list[MuscleGroupRead])
def list_muscle_groups(db:Session= Depends(get_db)):
    statement= select(MuscleGroup).order_by(MuscleGroup.name)
    return db.execute(statement).scalars().all()