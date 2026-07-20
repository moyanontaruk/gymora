# SQLAlchemy models are imported here for Alembic discovery.

from app.models.user import User
from app.models.equipment import Equipment
from app.models.muscle_group import MuscleGroup
from app.models.exercise import Exercise
from app.models.exercise_muscle_group import ExerciseMuscleGroup
from app.models.exercise_equipment import ExerciseEquipment
from app.models.routine import Routine
from app.models.workout_log import WorkoutLog
from app.models.workout_log_exercise import WorkoutLogExercise
from app.models.routine_exercise import RoutineExercise
from app.models.assistant_message import AssistantMessage


__all__ = [
    "User",
    "Equipment",
    "MuscleGroup",
    "Exercise",
    "ExerciseMuscleGroup",
    "ExerciseEquipment",
    "Routine",
    "WorkoutLog",
    "WorkoutLogExercise",
    "RoutineExercise",
    "AssistantMessage",
]