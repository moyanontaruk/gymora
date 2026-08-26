#AI generated and guided

#the rules half of routine generation
    #picks exercises from my own db and splits them across days
    #no LLM here, that's added separately in the router
    #same inputs always give the same routine, which makes it testable

from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload

from app.models.exercise import Exercise
from app.models.equipment import Equipment
from app.models.exercise_equipment import ExerciseEquipment
from app.models.muscle_group import MuscleGroup
from app.models.exercise_muscle_group import ExerciseMuscleGroup


#these numbers are conventional gym practice, not clinically validated
    #noting that as a limitation in the dissertation


#how the week gets split, based on days per week
    #each list is one day, holding the muscle groups to hit that day
    #names must match my muscle_groups table exactly
SPLITS = {
    1: [
        ["Chest", "Back", "Quadriceps", "Core"],
    ],
    2: [
        ["Chest", "Shoulders", "Triceps"],
        ["Back", "Biceps", "Quadriceps"],
    ],
    3: [
        ["Chest", "Shoulders", "Triceps"],
        ["Back", "Biceps"],
        ["Quadriceps", "Hamstrings", "Glutes", "Calves"],
    ],
    4: [
        ["Chest", "Triceps"],
        ["Back", "Biceps"],
        ["Quadriceps", "Hamstrings", "Glutes"],
        ["Shoulders", "Core"],
    ],
    5: [
        ["Chest", "Triceps"],
        ["Back", "Biceps"],
        ["Quadriceps", "Hamstrings"],
        ["Shoulders", "Core"],
        ["Glutes", "Calves", "Core"],
    ],
    6: [
        ["Chest", "Triceps"],
        ["Back", "Biceps"],
        ["Quadriceps", "Hamstrings", "Glutes"],
        ["Shoulders", "Core"],
        ["Chest", "Back"],
        ["Quadriceps", "Calves"],
    ],
    7: [
        ["Chest", "Triceps"],
        ["Back", "Biceps"],
        ["Quadriceps", "Hamstrings"],
        ["Shoulders", "Core"],
        ["Glutes", "Calves"],
        ["Chest", "Back"],
        ["Core"],
    ],
}


#sets, reps and rest depend on the goal
    #strength = heavy and few reps, endurance = light and many
SETS_AND_REPS = {
    "muscle gain": {"sets": 3, "reps": "8-12", "rest": 90},
    "strength": {"sets": 4, "reps": "4-6", "rest": 150},
    "fat loss": {"sets": 3, "reps": "12-15", "rest": 45},
    "general fitness": {"sets": 3, "reps": "10-12", "rest": 60},
}

#used if the goal doesn't match anything above
DEFAULT_SETS_AND_REPS = {"sets": 3, "reps": "10-12", "rest": 60}


#roughly how many exercises fit in a session
    #a set plus rest is about 2 minutes, so this is session length
    #divided by sets times 2, rounded to something sensible
EXERCISES_PER_SESSION = {
    30: 4,
    45: 5,
    60: 6,
    90: 8,
}


def exercises_per_day(session_length_minutes: int) -> int:

    #find the closest option that isn't longer than what they picked..
    best = 4

    for length in sorted(EXERCISES_PER_SESSION):
        if session_length_minutes >= length:
            best = EXERCISES_PER_SESSION[length]

    return best


def get_sets_and_reps(goal: str) -> dict:

    #.lower() so "Muscle Gain" and "muscle gain" both match..
    key = goal.lower().strip()

    #.get() with a default, so an unexpected goal doesn't crash..
    return SETS_AND_REPS.get(key, DEFAULT_SETS_AND_REPS)


def find_exercises_for_muscle(
    db: Session,
    muscle_name: str,
    equipment_names: list[str],
    experience_level: str,
    how_many: int,
    already_used: set,
) -> list:

    #builds the candidate list for one muscle group on one day..

    #counting how many muscle groups each exercise is tagged with.
        #wger data has some junk entries tagged with 7 or 8 muscles..
        #which match every query and crowd out the real ones.
        #a subquery is a query used INSIDE another query..
    muscle_count = (
        select(
            ExerciseMuscleGroup.exercise_id,
            func.count().label("how_many_muscles"),
        )
        .group_by(ExerciseMuscleGroup.exercise_id)

        #.subquery() turns it into something I can join to
    ).subquery()

    statement = (
        select(Exercise)
        .join(ExerciseMuscleGroup, ExerciseMuscleGroup.exercise_id == Exercise.exercise_id)
        .join(MuscleGroup, MuscleGroup.muscle_group_id == ExerciseMuscleGroup.muscle_group_id)

        #joining the count subquery so I can sort by it below
        .join(muscle_count, muscle_count.c.exercise_id == Exercise.exercise_id)

        .where(
            MuscleGroup.name == muscle_name,
            Exercise.is_active == True,

            #only exercises where this muscle is a PRIMARY target,
                #not one that's incidentally involved.
                #wger marks this and my import script stored it
            ExerciseMuscleGroup.is_primary == True,
        )

        .options(
            selectinload(Exercise.muscle_groups),
            selectinload(Exercise.equipment),
        )
    )

    #only filter on equipment if they told me what they have
    if equipment_names:
        statement = (
            statement
            .join(ExerciseEquipment, ExerciseEquipment.exercise_id == Exercise.exercise_id)
            .join(Equipment, Equipment.equipment_id == ExerciseEquipment.equipment_id)
            .where(Equipment.name.in_(equipment_names))
        )

    #.in_() is sqlalchemy for sql's IN, so "name is any of these"

    statement = (
        statement

        #no .distinct() here. postgres won't allow ordering by a
            #subquery column when using SELECT DISTINCT, so duplicates
            #get removed in python further down instead

        #fewest muscle groups first. an exercise tagged with 2 muscles
            #is far more likely to be a real chest exercise than one
            #tagged with 7. .c. is how you read a column off a subquery
        .order_by(muscle_count.c.how_many_muscles, Exercise.name)
    )

    candidates = db.execute(statement).scalars().all()

    #if primary-only found nothing, fall back to any link.
        #some muscle groups may have no primary tagged exercises at all,
        #and an empty day is worse than an imperfect one..
    if not candidates:
        fallback = (
            select(Exercise)
            .join(ExerciseMuscleGroup, ExerciseMuscleGroup.exercise_id == Exercise.exercise_id)
            .join(MuscleGroup, MuscleGroup.muscle_group_id == ExerciseMuscleGroup.muscle_group_id)
            .join(muscle_count, muscle_count.c.exercise_id == Exercise.exercise_id)
            .where(
                MuscleGroup.name == muscle_name,
                Exercise.is_active == True,
            )
            .options(
                selectinload(Exercise.muscle_groups),
                selectinload(Exercise.equipment),
            )

            #no .distinct() here either, same postgres restriction
            .order_by(muscle_count.c.how_many_muscles, Exercise.name)
        )

        if equipment_names:
            fallback = (
                fallback
                .join(ExerciseEquipment, ExerciseEquipment.exercise_id == Exercise.exercise_id)
                .join(Equipment, Equipment.equipment_id == ExerciseEquipment.equipment_id)
                .where(Equipment.name.in_(equipment_names))
            )

        candidates = db.execute(fallback).scalars().all()

    #sort so exercises matching their experience level come first,
        #then unrated ones, then everything else.
        #a sort not a filter, b/c most wger imports have no difficulty
        #and filtering would leave me with almost nothing
    wanted_level = experience_level.lower().strip()

    def sort_key(exercise):
        level = (exercise.difficulty_level or "").lower()

        if level == wanted_level:
            return 0

        if level == "":
            return 1

        return 2

    candidates = sorted(candidates, key=sort_key)

    #take the first few that haven't been used elsewhere in this
        #routine, so nothing appears twice
    chosen = []
    seen = set()

    for exercise in candidates:

        if len(chosen) >= how_many:
            break

        #the joins can return the same exercise more than once, and
            #.distinct() can't be used in the query for the reason
            #above, so duplicates are filtered out here instead
        if exercise.exercise_id in seen:
            continue

        seen.add(exercise.exercise_id)

        if exercise.exercise_id in already_used:
            continue

        chosen.append(exercise)
        already_used.add(exercise.exercise_id)

    return chosen


def generate_routine(db: Session, request) -> list:

    #the main function. returns a list of dicts, one per exercise,
        #each carrying its day number and order.
        #the router turns these into schema objects

    #.get() with a fallback, in case days_per_week is somehow outside
        #1 to 7 despite the schema validation
    split = SPLITS.get(request.days_per_week, SPLITS[3])

    per_day = exercises_per_day(request.session_length_minutes)
    prescription = get_sets_and_reps(request.goal)

    #a set, so checking "have I used this already" is fast.
        #shared across ALL days, so no exercise repeats in the routine
    already_used = set()

    plan = []

    #enumerate with start=1 so days are numbered 1, 2, 3 not 0, 1, 2
    for day_number, muscles_today in enumerate(split, start=1):

        order = 1

        #work out how many exercises each muscle group gets today.
            #integer division // rounds down, then max(1, ...) makes
            #sure every muscle gets at least one
        per_muscle = max(1, per_day // len(muscles_today))

        for muscle_name in muscles_today:

            found = find_exercises_for_muscle(
                db=db,
                muscle_name=muscle_name,
                equipment_names=request.equipment,
                experience_level=request.experience_level,
                how_many=per_muscle,
                already_used=already_used,
            )

            for exercise in found:

                plan.append({
                    "exercise": exercise,
                    "day_number": day_number,
                    "exercise_order": order,
                    "suggested_sets": prescription["sets"],
                    "suggested_reps": prescription["reps"],
                    "rest_seconds": prescription["rest"],
                })

                order = order + 1

    return plan