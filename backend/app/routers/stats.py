from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.workout_log import WorkoutLog
from app.models.workout_log_exercise import WorkoutLogExercise
from app.models.exercise import Exercise
from app.models.muscle_group import MuscleGroup
from app.models.exercise_muscle_group import ExerciseMuscleGroup
from app.schemas.stats import ProfileStats, MuscleGroupStat, ExerciseStat
from app.core.dependencies import get_current_user


router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/profile", response_model=ProfileStats)
def profile_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    user_id = current_user.user_id

    #total workouts logged
        #scalar() returns a single value rather than rows,
        #which is what count queries give back
    total_workouts = db.execute(
        select(func.count(WorkoutLog.workout_log_id))
        .where(WorkoutLog.user_id == user_id)
    ).scalar()

    #total exercise rows across all workouts
    total_exercises = db.execute(
        select(func.count(WorkoutLogExercise.workout_log_exercise_id))
        .join(WorkoutLog, WorkoutLog.workout_log_id == WorkoutLogExercise.workout_log_id)
        .where(WorkoutLog.user_id == user_id)
    ).scalar()

    #workouts since the 1st of this month.
        #date.today().replace(day=1) gives the first of the current month
    month_start = date.today().replace(day=1)

    workouts_this_month = db.execute(
        select(func.count(WorkoutLog.workout_log_id))
        .where(
            WorkoutLog.user_id == user_id,
            WorkoutLog.workout_date >= month_start,
        )
    ).scalar()

    #muscle group breakdown. same four joins as the assistant uses
    muscle_rows = db.execute(
        select(
            MuscleGroup.name,
            func.count(WorkoutLog.workout_log_id),
        )
        .join(WorkoutLogExercise, WorkoutLogExercise.workout_log_id == WorkoutLog.workout_log_id)
        .join(Exercise, Exercise.exercise_id == WorkoutLogExercise.exercise_id)
        .join(ExerciseMuscleGroup, ExerciseMuscleGroup.exercise_id == Exercise.exercise_id)
        .join(MuscleGroup, MuscleGroup.muscle_group_id == ExerciseMuscleGroup.muscle_group_id)
        .where(WorkoutLog.user_id == user_id)
        .group_by(MuscleGroup.name)
        .order_by(func.count(WorkoutLog.workout_log_id).desc())
    ).all()

    muscle_groups = []

    for name, times in muscle_rows:
        muscle_groups.append(MuscleGroupStat(name=name, times_trained=times))

    #the most trained exercises, with the heaviest weight used
    exercise_rows = db.execute(
        select(
            Exercise.name,
            func.max(WorkoutLogExercise.weight),
            func.count(WorkoutLogExercise.workout_log_exercise_id),
        )
        .join(WorkoutLogExercise, WorkoutLogExercise.exercise_id == Exercise.exercise_id)
        .join(WorkoutLog, WorkoutLog.workout_log_id == WorkoutLogExercise.workout_log_id)
        .where(WorkoutLog.user_id == user_id)
        .group_by(Exercise.name)
        .order_by(func.count(WorkoutLogExercise.workout_log_exercise_id).desc())

        #only the top 5 since the page shows a short list
        .limit(5)
    ).all()

    top_exercises = []

    for name, best_weight, times in exercise_rows:
        top_exercises.append(
            ExerciseStat(
                name=name,

                #weight comes back as a Decimal from postgres.
                    #float() converts it, and the check handles
                    #exercises logged without any weight
                best_weight=float(best_weight) if best_weight is not None else None,

                times_performed=times,
            )
        )

    #the muscle group trained most recently
    last_row = db.execute(
        select(MuscleGroup.name)
        .join(ExerciseMuscleGroup, ExerciseMuscleGroup.muscle_group_id == MuscleGroup.muscle_group_id)
        .join(Exercise, Exercise.exercise_id == ExerciseMuscleGroup.exercise_id)
        .join(WorkoutLogExercise, WorkoutLogExercise.exercise_id == Exercise.exercise_id)
        .join(WorkoutLog, WorkoutLog.workout_log_id == WorkoutLogExercise.workout_log_id)
        .where(WorkoutLog.user_id == user_id)
        .order_by(WorkoutLog.workout_date.desc())
        .limit(1)
    ).scalar_one_or_none()

    return ProfileStats(
        username=current_user.username,
        email=current_user.email,

        #.isoformat() turns a date into "2026-08-20" text
        member_since=current_user.created_at.date().isoformat(),

        total_workouts=total_workouts,
        total_exercises_performed=total_exercises,
        workouts_this_month=workouts_this_month,
        muscle_groups=muscle_groups,
        top_exercises=top_exercises,
        last_trained=last_row,
    )