from app.database import Base
from sqlalchemy import ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column


class ExerciseMuscleGroup(Base):
    __tablename__ = "exercise_muscle_group"

    exercise_muscle_group_id: Mapped[int] = mapped_column(primary_key=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.exercise_id", nullable = False))
    muscle_group_id: Mapped[int] = mapped_column(ForeignKey("muscle_groups.muscle_group_id", nullable = False))
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable= False, default = False)
