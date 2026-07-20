from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from app.database import Base

class ExerciseEquipment(Base):
    __tablename__ = "exercise_equipment"

    exercise_equipment_id: Mapped[int] = mapped_column(primary_key=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.exercise_id"), nullable=False)
    equipment_id: Mapped[int]= mapped_column(ForeignKey("equipment.equipment_id"),nullable=False)