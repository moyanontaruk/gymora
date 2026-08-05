from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.schemas.muscle_group import MuscleGroupRead
from app.schemas.equipment import EquipmentRead

class ExerciseBase(BaseModel):
    name: str
    description: str | None = None
    instructions: str | None = None
    difficulty_level: str | None = None
    exercise_type: str | None = None
    source: str | None = None
    source_external_id: str | None = None
    media_url: str | None = None
    is_active: bool = True


class ExerciseCreate(ExerciseBase):
    pass

class ExerciseRead(ExerciseBase):
    exercise_id: int
    created_at: datetime
    updated_at: datetime | None = None
    created_by_user_id: int | None = None

    muscle_groups:list[MuscleGroupRead] = []
    equipment:list[EquipmentRead] = []


#need this line for pydantic to go into exercise object, pull out whatevr & turns into clean JSON
#w/o this line, it was throw an error
    model_config = ConfigDict(from_attributes=True)

class ExerciseUpdate(BaseModel):
    name: str
    description: str | None = None
    instructions: str | None = None
    difficulty_level: str | None = None
    exercise_type: str | None = None
    source: str | None = None
    source_external_id: str | None = None
    media_url: str | None = None
    is_active: bool = True
