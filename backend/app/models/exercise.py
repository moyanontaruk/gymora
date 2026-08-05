from app.database import Base
from datetime import datetime
from sqlalchemy import Text, String, DateTime, ForeignKey, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Exercise(Base):
    __tablename__ = "exercises"

    exercise_id: Mapped[int] = mapped_column(primary_key= True)
    name: Mapped[str] = mapped_column(String(200), nullable= False)
    description: Mapped[str | None ] = mapped_column(Text, nullable= True)
    instructions: Mapped[str | None] = mapped_column(Text, nullable= True)
    difficulty_level: Mapped[str | None] = mapped_column(String(50), nullable= True)
    exercise_type: Mapped[str | None] = mapped_column(String(50), nullable= True)
    source: Mapped[str | None] = mapped_column(String(50), nullable= True)
    source_external_id: Mapped[str | None] = mapped_column(String(100), nullable= True)
    media_url: Mapped[str | None] = mapped_column(String(500), nullable= True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.user_id"), nullable= True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone= True),
        nullable=False, 
        server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable= True, onupdate=func.now())


    #not columns but hop THROUGH the join tables automatic
    muscle_groups: Mapped[list["MuscleGroup"]] = relationship(

        #secondary = shortcut for many-to-many 
            # also names the middle table to get muscle group directly
                #instead of getting join rows and then looking each one up
        secondary= "exercise_muscle_group",

        viewonly=True,

        order_by="MuscleGroup.name"
    )

    equipment: Mapped[list["Equipment"]] = relationship(
        secondary="exercise_equipment",

        viewonly=True,
        order_by="Equipment.name"
    )

