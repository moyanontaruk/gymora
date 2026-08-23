from pydantic import BaseModel


#one muscle group and how much it's been trained
class MuscleGroupStat(BaseModel):
    name: str
    times_trained: int


#one exercise and its best weight
class ExerciseStat(BaseModel):
    name: str
    best_weight: float | None = None
    times_performed: int


#the whole profile summary
class ProfileStats(BaseModel):
    username: str
    email: str
    member_since: str

    #the headline numbers
    total_workouts: int
    total_exercises_performed: int
    workouts_this_month: int

    #the breakdowns
    muscle_groups: list[MuscleGroupStat] = []
    top_exercises: list[ExerciseStat] = []

    #the most recently trained muscle group, or None if nothing logged
    last_trained: str | None = None