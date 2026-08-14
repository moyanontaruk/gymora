#RETRIEVAL HALF OF RAG~~~~
    #queries user's own rows and formats them as plain text.
    #no LLM here
        #just sql and string building

from datetime import date, timedelta

from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload

from app.config import get_settings
from app.models.workout_log import WorkoutLog
from app.models.workout_log_exercise import WorkoutLogExercise
from app.models.exercise import Exercise
from app.models.muscle_group import MuscleGroup
from app.models.exercise_muscle_group import ExerciseMuscleGroup


settings = get_settings()


#1 - recent workouts

def recent_workouts_text(db: Session, user_id: int) -> str:

    #timedelta is a duration.
        #today minus 30 days... =the cutoff date.
    cutoff = date.today() - timedelta(days=settings.assistant_history_days)

    statement = (
        select(WorkoutLog)

        #TWO conditions: this user's rows and recent enough.
            #the user_id line is stops one user's data
                #from ever reaching another user's assistant
        .where(
            WorkoutLog.user_id == user_id,
            WorkoutLog.workout_date >= cutoff,
        )

        #load the exercise rows & the exercises they point at,
            #so that names will be printed instead of ids
        .options(
            selectinload(WorkoutLog.exercises)
            .selectinload(WorkoutLogExercise.exercise)
        )

        #oldest first so the text reads as a timeline
        .order_by(WorkoutLog.workout_date)
    )

    workouts = db.execute(statement).scalars().all()

    if not workouts:
        return "No workouts logged in this period."

    #building a list of lines.
        #then joining them at the end.
        #faster/cleaner than adding to a str on repeat.
    lines = []

    for workout in workouts:

        title = workout.title or "Workout"
        lines.append(f"{workout.workout_date} - {title}")

        for row in workout.exercises:

            #the nested exercise might be missing so guard it.
            name = row.exercise.name if row.exercise else f"Exercise {row.exercise_id}"

            #building up the detail one at a time.
                #only include what was actually recorded.
            details = []

            if row.sets is not None and row.reps is not None:
                details.append(f"{row.sets} sets x {row.reps} reps")

            if row.weight is not None:
                details.append(f"{row.weight}kg")

            if details:
                #", ".join puts a comma between each item.
                lines.append(f"  - {name}: {', '.join(details)}")
            else:
                lines.append(f"  - {name}")

    #"\n" =newline so join puts one between every line.
    return "\n".join(lines)





# 2-- muscle group balance..

def muscle_group_text(db: Session, user_id: int) -> str:

    cutoff = date.today() - timedelta(days=settings.assistant_history_days)

    statement = (
        #selecting 3 things... not whole objects:
            #the muscle group name + how many times it appears + and the most recent date it was trained
        #func.count and func.max are sql functions run by postgres,
            #much faster than fetching everything and counting it here
        select(
            MuscleGroup.name,
            func.count(WorkoutLog.workout_log_id),
            func.max(WorkoutLog.workout_date),
        )

        #4 joins... walking from workouts -> to muscle names:
            #workout_log -> workout_log_exercise -> exercises -> exercise_muscle_group -> muscle_groups
        .join(WorkoutLogExercise, WorkoutLogExercise.workout_log_id == WorkoutLog.workout_log_id)
        .join(Exercise, Exercise.exercise_id == WorkoutLogExercise.exercise_id)
        .join(ExerciseMuscleGroup, ExerciseMuscleGroup.exercise_id == Exercise.exercise_id)
        .join(MuscleGroup, MuscleGroup.muscle_group_id == ExerciseMuscleGroup.muscle_group_id)

        #confirming again the IDs match up
        .where(
            WorkoutLog.user_id == user_id,
            WorkoutLog.workout_date >= cutoff,
        )

        #group_by = "give me one row per muscle group",
            #with the count and max calculated within each group
        .group_by(MuscleGroup.name)

        #.desc() = highest count first
        .order_by(func.count(WorkoutLog.workout_log_id).desc())
    )

    #.all() not .scalars().all() b/c each row has 3 values.
        #not one object so each result is a tuple I can unpack.
    results = db.execute(statement).all()

    if not results:
        return "No muscle group data available."

    lines = []

    #unpacking 3 values from each row at once-
    for name, times, last_date in results:
        lines.append(f"{name}: trained {times} times, most recently {last_date}")

    return "\n".join(lines)


# 3-strength progression-

def progression_text(db: Session, user_id: int) -> str:

    cutoff = date.today() - timedelta(days=settings.assistant_history_days)

    statement = (
        #for each exercise on each date + the heaviest weight used
        select(
            Exercise.name,
            WorkoutLog.workout_date,
            func.max(WorkoutLogExercise.weight),
        )
        .join(WorkoutLogExercise, WorkoutLogExercise.workout_log_id == WorkoutLog.workout_log_id)
        .join(Exercise, Exercise.exercise_id == WorkoutLogExercise.exercise_id)

        .where(
            WorkoutLog.user_id == user_id,
            WorkoutLog.workout_date >= cutoff,

            #only rows where a weight was actually recorded.
            WorkoutLogExercise.weight.is_not(None),
        )

        #one row per exercise per date
        .group_by(Exercise.name, WorkoutLog.workout_date)
        .order_by(Exercise.name, WorkoutLog.workout_date)
    )

    results = db.execute(statement).all()

    if not results:
        return "No weight data recorded."

    lines = []

    for name, workout_date, top_weight in results:
        lines.append(f"{name} on {workout_date}: {top_weight}kg")

    return "\n".join(lines)



#ALL TOGETHER NOW (we all sing in unison)...

def build_context(db: Session, user_id: int) -> str:

    #heading. =they tell the model what each block is..
        #which makes it better at picking the right one..
    return f"""RECENT WORKOUTS (last {settings.assistant_history_days} days):
{recent_workouts_text(db, user_id)}

MUSCLE GROUPS TRAINED:
{muscle_group_text(db, user_id)}

WEIGHT PROGRESSION:
{progression_text(db, user_id)}

TODAY'S DATE: {date.today()}"""






#temp dev tool
# if __name__ == "__main__":
#     from app.database import SessionLocal
#     db = SessionLocal()
#     print(build_context(db, 5))   # use your own user_id
#     db.close()