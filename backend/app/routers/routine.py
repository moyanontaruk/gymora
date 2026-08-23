from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.user import User
from app.models.routine import Routine
from app.models.routine_exercise import RoutineExercise
from app.schemas.routine import (
    RoutineGenerateRequest,
    RoutineGenerated,
    RoutineExerciseRead,
    RoutineCreate,
    RoutineRead,
    RoutineSummary,
)
from app.core.dependencies import get_current_user
from app.services.routine_generator import generate_routine
from app.services.llm import ask_llm, LLMError


router = APIRouter(prefix="/routines", tags=["routines"])


#the rules pick the exercises, this asks the LLM to explain why
    #keeping them separate means the routine itself is always the same
    #for the same inputs, only the wording varies
#used AI to help create rules
EXPLANATION_PROMPT = """You are Gymora's fitness assistant, helping
someone new to the gym understand a training plan.

You will be given a person's preferences and a routine that has already
been built for them. Write a short, friendly explanation of why the
routine looks the way it does.

RULES:
1. Only describe the routine you are given. Never add or rename exercises.
2. Explain the split, why that many days suits their goal, and why the
   sets and reps were chosen.
3. Keep it under 120 words. Avoid jargon, and explain any term you use.
4. Do not give medical advice or nutrition advice.
5. Write in plain, encouraging language for a beginner."""


#helper so the same ownership check isn't written three times
def get_owned_routine(routine_id: int, db: Session, current_user: User) -> Routine:

    statement = (
        select(Routine)
        .where(Routine.routine_id == routine_id)
        .options(
            selectinload(Routine.exercises)
            .selectinload(RoutineExercise.exercise)
        )
    )

    routine = db.execute(statement).scalar_one_or_none()

    #same 404 for "doesn't exist" and "not yours", so nobody can
        #count upwards through ids to find out what exists
    if routine is None or routine.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Routine not found",
        )

    return routine


@router.post("/generate", response_model=RoutineGenerated)
def generate(
    payload: RoutineGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    #step 1--the rules pick the exercises
    plan = generate_routine(db, payload)

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough exercises match those options. Try selecting different combinations.",
        )

    #step 2-- turn the plan into schema objects
    exercises = []

    for item in plan:
        exercises.append(
            RoutineExerciseRead(
                exercise_id=item["exercise"].exercise_id,
                day_number=item["day_number"],
                exercise_order=item["exercise_order"],
                suggested_sets=item["suggested_sets"],
                suggested_reps=item["suggested_reps"],
                rest_seconds=item["rest_seconds"],

                #model_validate turns a sqlalchemy object into a
                    #pydantic one. needed b/c I'm building this by hand
                    #instead of letting fastapi do it from a db row
                exercise=item["exercise"],
            )
        )

    #step 3-- build a plain text summary for the LLM to explain.
        #only the bits it needs, not the whole exercise objects
    summary_lines = []

    for item in plan:
        summary_lines.append(
            f"Day {item['day_number']}: {item['exercise'].name}, "
            f"{item['suggested_sets']} sets of {item['suggested_reps']}"
        )

    user_message = f"""PREFERENCES:
Goal: {payload.goal}
Experience: {payload.experience_level}
Days per week: {payload.days_per_week}
Session length: {payload.session_length_minutes} minutes
Equipment available: {", ".join(payload.equipment) or "any"}

THE ROUTINE:
{chr(10).join(summary_lines)}"""

    #step 4-- ask for the explanation.
        #if the LLM is down the routine is still perfectly usable,
        #so this failure is caught and ignored rather than raised
    explanation = None

    try:
        explanation = ask_llm(EXPLANATION_PROMPT, user_message)
    except LLMError:
        explanation = None

    #readable default name, the user can change it before saving
    name = f"{payload.days_per_week} day {payload.goal} routine"

    #nothing has been saved. this is just handed back
    return RoutineGenerated(
        name=name,
        goal=payload.goal,
        experience_level=payload.experience_level,
        days_per_week=payload.days_per_week,
        session_length_minutes=payload.session_length_minutes,
        target_muscle_group_id=payload.target_muscle_group_id,
        exercises=exercises,
        explanation=explanation,
    )


@router.post("/", response_model=RoutineRead, status_code=status.HTTP_201_CREATED)
def save_routine(
    payload: RoutineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    routine = Routine(
        #from the token, never from the payload
        user_id=current_user.user_id,

        name=payload.name,
        goal=payload.goal,
        experience_level=payload.experience_level,
        days_per_week=payload.days_per_week,
        session_length_minutes=payload.session_length_minutes,
        target_muscle_group_id=payload.target_muscle_group_id,

        #this is the whole point of the two step flow. a routine
            #only exists in the db once the user chose to keep it
        is_saved=True,
    )

    for row in payload.exercises:
        routine.exercises.append(
            RoutineExercise(
                exercise_id=row.exercise_id,
                day_number=row.day_number,
                exercise_order=row.exercise_order,
                suggested_sets=row.suggested_sets,
                suggested_reps=row.suggested_reps,
                rest_seconds=row.rest_seconds,
                notes=row.notes,
            )
        )

    #only the parent is added, the cascade saves the children
    db.add(routine)
    db.commit()
    db.refresh(routine)

    return routine


@router.get("/", response_model=list[RoutineSummary])
def list_routines(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    statement = (
        select(Routine)

        #only this user's routines
        .where(Routine.user_id == current_user.user_id)

        #newest first
        .order_by(Routine.created_at.desc())
    )

    return db.execute(statement).scalars().all()


@router.get("/{routine_id}", response_model=RoutineRead)
def get_routine(
    routine_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_owned_routine(routine_id, db, current_user)


@router.delete("/{routine_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_routine(
    routine_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    routine = get_owned_routine(routine_id, db, current_user)

    db.delete(routine)
    db.commit()
    return None