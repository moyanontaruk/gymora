from datetime import date, datetime
from pydantic import BaseModel, ConfigDict

## bigger than equipment because workout = 2 things
    #1. workout itself (PARENT) 
    #2. the exercise inside it (CHILD).. this one is first
#... so writing 2 set of schemas. child + parent 


#the child>> one exercise performed inside a workout 
class WorkoutLogExerciseBase(BaseModel):

    exercise_id: int

    #below optional. not every workout records weight or duration blah blah
    sets: int | None = None
    reps: int | None = None
    weight: float | None = None
    duration_minutes: int | None = None
    exercise_order: int | None = None
    notes: str | None = None


#what the client sends for each exercise row
#no ids here, the db makes those
class WorkoutLogExerciseCreate(WorkoutLogExerciseBase):
    pass


#what the api sends back for each exercise row
class WorkoutLogExerciseRead(WorkoutLogExerciseBase):
    workout_log_exercise_id: int
    workout_log_id: int

#need this line for pydantic to go into workout log object, pull out whatevr & turns into clean JSON
#w/o this line, it was throw an error
    model_config = ConfigDict(from_attributes=True)





#PARENT.. the whole workout itself 
class WorkoutLogBase(BaseModel):

    # matches Date column in the model
    workout_date: date

    title: str | None = None
    notes: str | None = None


#what the client sends to create a whole workout
class WorkoutLogCreate(WorkoutLogBase):

    #a field whose type is a LIST of another schema. this is the nesting
    #default empty list = client can save a workout and add exercises later
    exercises: list[WorkoutLogExerciseCreate] = []


#what the api sends back
class WorkoutLogRead(WorkoutLogBase):
    workout_log_id: int

    #included so the client can see ownership, but never accepted as input
        #or else anyone could add a log to another person's account
            #passed the test when i ran the server. user1 adds log which is given a logID 
                #user2 cannot find that logID because they have different userID
    user_id: int
    created_at: datetime
    updated_at: datetime | None = None

    #the child rows come back nested inside the parent
        #schema used as type of field inside another schema 
    exercises: list[WorkoutLogExerciseRead] = []


    model_config = ConfigDict(from_attributes=True)


#all optional, so the client can send only the fields that changed
class WorkoutLogUpdate(BaseModel):
    workout_date: date | None = None
    title: str | None = None
    notes: str | None = None