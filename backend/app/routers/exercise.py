from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session,selectinload
from app.database import get_db
from app.models.exercise import Exercise
from app.schemas.exercise import ExerciseCreate, ExerciseRead, ExerciseUpdate


from app.models.muscle_group import MuscleGroup
from app.models.equipment import Equipment
from app.models.exercise_muscle_group import ExerciseMuscleGroup
from app.models.exercise_equipment import ExerciseEquipment
from app.models.user import User
from app.core.dependencies import get_current_admin


router = APIRouter(prefix="/exercises",tags=["exercises"])


#post=create a path / so POST /equipment/
# shape it using EquipmentRead schema before sending back
@router.post("/", response_model=ExerciseRead, status_code=status.HTTP_201_CREATED)

#payload tells FastAPI the income request must match the equip schema shape. 
    #client sends over JSON but FastAPI will reject if not correct shape before function even runs
def create_exercise(payload: ExerciseCreate, 
                    db: Session = Depends(get_db), 
                    current_admin: User =Depends(get_current_admin),):


    #creating new instance of model(db object)
    #filling in the fields from EquipmentCreate with the validated payload shape.
    
    #ignore anything the client sent, the server decides from the token
    data = payload.model_dump()
    data["created_by_user_id"] = current_admin.user_id

    exercise = Exercise(**data)
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
    difficulty_level: str | None = None,
    exercise_type: str | None = None,

    #these two filter THROUGH the join tables
    muscle_group: str | None = None,
    equipment: str | None = None,

    #free text search on the name
    search: str | None = None,

    #don't hand back 72+ rows at once
    limit: int = 50,
    offset: int = 0,



    db:Session = Depends(get_db)):
 
    #select all exercise that havn't been turned off
    statement = select(Exercise).where(Exercise.is_active == True)

    #each filter below adds to the statement, it wont run until the end
    if search is not None:
        #ilike = case insensitive
        #% = means "any character here" that matches that. 
            #so like.. if search is "bench".... "barbell bench press" will also show
        statement = statement.where(Exercise.name.ilike("%" + search + "%"))

    #only add filter if client sent one
    if difficulty_level is not None:
        #where the exc. diff_level columns = the value the client selected
        statement = statement.where(Exercise.difficulty_level == difficulty_level)

    if exercise_type is not None:
        statement = statement.where(Exercise.exercise_type == exercise_type)





    #two joins to get from exercises to a muscle group NAME
        # exercise -> exercise_muscle_group-> muscle_groups
    if muscle_group is not None:
        statement = (
            statement

            #hop 1: exercises -> the join table, matching on exercise_id
            .join(
                ExerciseMuscleGroup,
                ExerciseMuscleGroup.exercise_id == Exercise.exercise_id,
            )

            #hop 2: join table -> muscle_groups, so I can read the name
            .join(
                MuscleGroup,
                MuscleGroup.muscle_group_id == ExerciseMuscleGroup.muscle_group_id,
            )

            .where(MuscleGroup.name.ilike(muscle_group))
        )

    #same two hop pattern for equipment
    if equipment is not None:
        statement = (
            statement
            .join(
                ExerciseEquipment,
                ExerciseEquipment.exercise_id == Exercise.exercise_id,
            )
            .join(
                Equipment,
                Equipment.equipment_id == ExerciseEquipment.equipment_id,
            )
            .where(Equipment.name.ilike(equipment))
        )

    statement = (
        statement

        #adding this block b/c w/o it returning 50 exercises willfire 101 queries
            #1 for list and 2 per exercise
        .options(
            selectinload(Exercise.muscle_groups),
            selectinload(Exercise.equipment),
        )

        #safety net. joins can return the same exercise more than once
        .distinct()

        #alphabetical so db wont return random order
        .order_by(Exercise.name)

        .limit(limit)
        .offset(offset)
    )



    results = db.execute(statement).scalars().all()
    return results


#get {} =path.. so get specific path id
@router.get("/{exercise_id}", response_model=ExerciseRead)
def get_exercise(exercise_id: int, db: Session = Depends(get_db)):


## changed from exercise = db.get(Exercise, exercise_id)
    #b/c db.get() has no parameter so when we need to pull muscle group, equpment, etc
        #sqlalchemy will get exercise, then pydantic reads muscle_groups for the response..
            #fires a 2nd query, 3rd, etc
    statement = (select(Exercise)
                .where(Exercise.exercise_id == exercise_id)
                .options(
                    selectinload(Exercise.muscle_groups),
                    selectinload(Exercise.equipment),
                ))
    exercise = db.execute(statement).scalar_one_or_none()

    if exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found",
        )
    return exercise

#put = means to update
@router.put("/{exercise_id}",response_model=ExerciseRead)
def update_exercise(exercise_id: int, 
                     payload: ExerciseUpdate, 
                     db:Session = Depends(get_db),
                     current_admin: User = Depends(get_current_admin),):
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

        #writing this way since I don't know the field names ahead of time
        setattr(exercise, field, value)

    db.commit()
    db.refresh(exercise)
    return exercise

#no response_model becaue nothing comes back, it'll just say 204 meaning success code
@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise(exercise_id: int, 
                    db: Session = Depends(get_db),
                    current_admin: User = Depends(get_current_admin),):
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