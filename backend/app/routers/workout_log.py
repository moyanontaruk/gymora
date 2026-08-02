from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.user import User
from app.models.workout_log import WorkoutLog
from app.models.workout_log_exercise import WorkoutLogExercise
from app.schemas.workout_log import (
    WorkoutLogCreate,
    WorkoutLogRead,
    WorkoutLogUpdate,
)

#the checkpoint. every endpoint below uses this to know WHO is asking
from app.core.dependencies import get_current_user


router = APIRouter(prefix="/workouts", tags=["workouts"])

#not an endpoint. no decorator, so it's never a url
#just a plain function the endpoints below call, so the rule is written once
def get_owned_workout(
    workout_log_id: int,
    db: Session,
    current_user: User,) -> WorkoutLog:

    workout = db.get(WorkoutLog, workout_log_id)

    #TWO failures, ONE response--
        #1. row doesn't exist at all
        #2. row exists but belongs to somebody else
    if workout is None or workout.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout log not found",
        )

    return workout



@router.post("/", response_model=WorkoutLogRead, status_code=status.HTTP_201_CREATED)
def create_workout_log(
    payload: WorkoutLogCreate,
    db: Session = Depends(get_db),

    #the new one. runs the whole token check, hands back the logged-in User
    current_user: User = Depends(get_current_user),
):

    workout = WorkoutLog(

        #from the TOKEN, never from the payload(user). client cannot choose this
        user_id=current_user.user_id,

        workout_date=payload.workout_date,
        title=payload.title,
        notes=payload.notes,
    )

    #enumerate = loop but also count. start=1 so counting begins at 1 not 0
    for index, exercise_payload in enumerate(payload.exercises, start=1):

        #.exercises is the relationship. appending here links the row automatically
        workout.exercises.append(
            WorkoutLogExercise(
                exercise_id=exercise_payload.exercise_id,
                sets=exercise_payload.sets,
                reps=exercise_payload.reps,
                weight=exercise_payload.weight,
                duration_minutes=exercise_payload.duration_minutes,

                #"or index" = if client didn't send an order, use loop position
                exercise_order=exercise_payload.exercise_order or index,

                notes=exercise_payload.notes,
            )
        )

    #only the PARENT is added. cascade saves the children too
    db.add(workout)
    db.commit()
    db.refresh(workout)
    return workout



@router.get("/", response_model=list[WorkoutLogRead])
def list_workout_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statement = (
        select(WorkoutLog)

        #NFR2 --only rows belonging to the logged-in user
        .where(WorkoutLog.user_id == current_user.user_id)

        #fetch all the child rows in ONE extra query instead of one per workout
        .options(selectinload(WorkoutLog.exercises))

        #newest workout first, matching WF
        .order_by(WorkoutLog.workout_date.desc())
    )

    results = db.execute(statement).scalars().all()
    return results





@router.get("/{workout_log_id}", response_model=WorkoutLogRead)
def get_workout_log(
    workout_log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    #helper fetch AND ownership check
    return get_owned_workout(workout_log_id, db, current_user)



@router.put("/{workout_log_id}", response_model=WorkoutLogRead)
def update_workout_log(
    workout_log_id: int,
    payload: WorkoutLogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workout = get_owned_workout(workout_log_id, db, current_user)

    #same rhythm as equipment.py. only fields the client actually sent
    updates = payload.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(workout, field, value)

    db.commit()
    db.refresh(workout)
    return workout


@router.delete("/{workout_log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout_log(
    workout_log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workout = get_owned_workout(workout_log_id, db, current_user)

    #deletes the child exercise rows too, because of the cascade
    db.delete(workout)
    db.commit()
    return None