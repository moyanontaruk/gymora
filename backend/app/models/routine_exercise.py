from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Text


class RoutineExercise(Base):
    __tablename__ = "routine_exercise"

    routine_exercise_id: Mapped[int] = mapped_column(primary_key=True)
    routine_id: Mapped[int] = mapped_column(ForeignKey("routine.routine_id"), nullable=False)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.exercise_id"), nullable=False)
    day_number: Mapped[int | None] = mapped_column(nullable=True)
    exercise_order: Mapped[int | None] = mapped_column(nullable=True)
    suggested_sets: Mapped[int | None] = mapped_column(nullable=True)
    suggested_reps: Mapped[str | None] = mapped_column(String(50), nullable=True)
    rest_seconds: Mapped[int | None] = mapped_column(nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    routine: Mapped["Routine"] = relationship(back_populates="exercises")

    #read only so I can show the exercise name not just the id
    exercise: Mapped["Exercise"] = relationship(viewonly=True)