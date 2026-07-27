from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.exercise import Exercise
from app.schemas.exercise import ExerciseCreate, ExerciseRead, ExerciseUpate

router = APIRouter(prefix="/exercises",tags=["exercises"])


#post=create a path / so POST /equipment/
# shape it using EquipmentRead schema before sending back
@router.post("/", response_model=ExerciseRead, status_code=status.HTTP_201_CREATED)

#payload tells FastAPI the income request must match the equip schema shape. 
    #client sends over JSON but FastAPI will reject if not correct shape before function even runs
def create_exercise(payload: ExerciseCreate, db: Session = Depends(get_db)):
    #creating new instance of model(db object)
    #filling in the fields from EquipmentCreate with the validated payload shape.
    
    #using**payload shortcut to avoid writing all the fields out since this is longer than equip.py
    exercise = Exercise(
        **payload.model_dump())
    #stage into session/i intend to save
    db.add(exercise)
    #write it into PostgreSQL, db assigns it's ID
    db.commit()
    #refresh so object knows it's ID
    db.refresh(exercise)
    return exercise

#get = read
#response_model = endpoint returning many items
@router.get("/", response_model=list[ExerciseRead])
def list_exercise(

    #adding these 2 query parameters 
    #each default is none because they are optional
    difficult_level: str | None = None,
    exercise_type: str | None = None,

    db:Session = Depends(get_db)):
 
    #select all exercise
    statement = select(Exercise)

    #only add filter if client sent one
    if difficult_level is not None:
        #where the exc. diff_level columns = the value the client selected
        statement = statement.where(Exercise.difficulty_level == difficult_level)

    if exercise_type is not None:
        statement = statement.where(Exercise.exercise_type == exercise_type)


    results = db.execute(statement).scalars().all()
    return results


#get {} =path.. so get specific path id
@router.get("/{exercise_id}", response_model=ExerciseRead)
def get_exercise(exercise_id: int, db: Session = Depends(get_db)):
    
    exercise = db.get(Exercise, exercise_id)
    if exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found",
        )
    return exercise

#put = means to update
@router.put("/{exercise_id}",response_model=ExerciseRead)
def update_equipment(exercise_id: int, payload: ExerciseUpate, db:Session = Depends(get_db)):
    exercise = db.get(Exercise, exercise_id)
    if exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail= "Exercise not found",
        )
    
    #model_dump = turns the incoming schema into plain dict.
    #exlude_unset=True -> only include fields the client actually sends
        #so they might only send description and no name so only keep that
        #without it, unset fields will update to blank/show None
    updates = payload.model_dump(exclude_unset=True)

    #loop over each field that the client sent and apply to obj. 
    for field, value in updates.items():
        setattr(exercise, field, value)

    db.commit()
    db.refresh(exercise)
    return exercise

#no response_model becaue nothing comes back, it'll just say 204 meaning success code
@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise(exercise_id: int, db: Session = Depends(get_db)):
    exercise = db.get(Exercise, exercise_id)
    if exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found",
        )

    #mark this row for removal
    db.delete(exercise)
    db.commit()
    return None