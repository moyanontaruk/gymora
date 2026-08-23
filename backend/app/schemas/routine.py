from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.exercise import ExerciseRead


#what the client sends to generate a routine
    #matches the preferences form, these are the inputs the rules use
class RoutineGenerateRequest(BaseModel):

    #Field(...) adds validation and the ... means required
        #this runs before my code so bad input never reaches the generator
    goal: str = Field(..., min_length=2, max_length=50)
    experience_level: str = Field(..., min_length=2, max_length=50)

    #ge = greater than or equal, le = less than or equal
        #stops someone asking for a 400 day per week routine
    days_per_week: int = Field(..., ge=1, le=7)

    session_length_minutes: int = Field(..., ge=15, le=180)

    #the equipment they have access to, by name
        #a list b/c someone can have several
        #default empty means no equipment filter, so use everything
    equipment: list[str] = []

    #optional, if set the routine leans towards this muscle group
    target_muscle_group_id: int | None = None


#one exercise inside a routine
class RoutineExerciseRead(BaseModel):
    exercise_id: int
    day_number: int | None = None
    exercise_order: int | None = None
    suggested_sets: int | None = None

    #a string not an int b/c reps are often a range like "8-12"
    suggested_reps: str | None = None

    rest_seconds: int | None = None
    notes: str | None = None

    #the full exercise nested in so the frontend gets names and
        #muscle groups without a second request
        #same pattern as WorkoutLogExerciseRead
    exercise: ExerciseRead | None = None

    model_config = ConfigDict(from_attributes=True)


#same shape but for sending to the save endpoint
    #no nested exercise here b/c the client shouldn't be sending back
    #a whole exercise object it didn't create
class RoutineExerciseCreate(BaseModel):
    exercise_id: int
    day_number: int | None = None
    exercise_order: int | None = None
    suggested_sets: int | None = None
    suggested_reps: str | None = None
    rest_seconds: int | None = None
    notes: str | None = None


#the generated routine, before it's saved
    #this is what /generate returns
    #note there's no routine_id b/c nothing has been written to the db yet
        #the client holds this, shows it, and only sends it to /save
        #if the user decides to keep it
class RoutineGenerated(BaseModel):
    name: str
    goal: str
    experience_level: str
    days_per_week: int
    session_length_minutes: int
    target_muscle_group_id: int | None = None

    exercises: list[RoutineExerciseRead] = []

    #the LLM's plain english explanation of why this routine looks
        #the way it does. this is the "reason" half of the hybrid
    explanation: str | None = None


#what the client sends to save
class RoutineCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    goal: str = Field(..., min_length=1, max_length=100)
    experience_level: str | None = None
    days_per_week: int | None = None
    session_length_minutes: int | None = None
    target_muscle_group_id: int | None = None

    exercises: list[RoutineExerciseCreate] = []


#what the api sends back for a saved routine
class RoutineRead(BaseModel):
    routine_id: int

    #included so the client can see ownership, never accepted as input
        #the server sets this from the token, same as workout logs
    user_id: int

    name: str
    goal: str
    experience_level: str | None = None
    days_per_week: int | None = None
    session_length_minutes: int | None = None
    target_muscle_group_id: int | None = None
    is_saved: bool
    created_at: datetime
    updated_at: datetime | None = None

    exercises: list[RoutineExerciseRead] = []

    model_config = ConfigDict(from_attributes=True)


#the list view, no exercises nested b/c the routines page only shows
    #name, goal and days per week. keeps the response small
class RoutineSummary(BaseModel):
    routine_id: int
    name: str
    goal: str
    experience_level: str | None = None
    days_per_week: int | None = None
    is_saved: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)