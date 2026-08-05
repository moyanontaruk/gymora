from pydantic import BaseModel, ConfigDict

class MuscleGroupBase(BaseModel):
    name:str
    description: str | None = None


class MuscleGroupRead(MuscleGroupBase):
    muscle_group_id: int

    model_config = ConfigDict(from_attributes=True)