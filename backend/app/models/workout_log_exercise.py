from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Numeric, Text


class WorkoutLogExercise(Base):
    __tablename__ = "workout_log_exercise"

    workout_log_exercise_id: Mapped[int] = mapped_column(primary_key=True)
    workout_log_id: Mapped[int] = mapped_column(ForeignKey("workout_log.workout_log_id"), nullable=False)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.exercise_id"), nullable=False)
    sets: Mapped[int | None] = mapped_column(nullable=True)
    reps: Mapped[int | None] = mapped_column(nullable=True)
    weight: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(nullable=True)
    exercise_order: Mapped[int | None] = mapped_column(nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)