from datetime import datetime
from pydantic import BaseModel, ConfigDict

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
    created_by_user_id: int | None = None

class ExerciseCreate(ExerciseBase):
    pass

class ExerciseRead(ExerciseBase):
    exercise_id: int
    created_at: datetime
    update_at: datetime | None = None


    model_config = ConfigDict(from_attributes=True)

class ExerciseUpate(BaseModel):
    name: str
    description: str | None = None
    instructions: str | None = None
    difficulty_level: str | None = None
    exercise_type: str | None = None
    source: str | None = None
    source_external_id: str | None = None
    media_url: str | None = None
    is_active: bool = True
    created_by_user_id: int | None = None