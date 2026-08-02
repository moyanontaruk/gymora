from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Date, DateTime, ForeignKey, String, Text, func
from datetime import datetime, date


class WorkoutLog(Base):
    __tablename__ = "workout_log"

    workout_log_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    workout_date: Mapped[date] = mapped_column(Date, nullable=False)
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    #not a column. tells SQLAlchemy that one workout has many exercise rows
    #Mapped[list[...]] = the python side will be a list of WorkoutLogExercise objects
    #quotes around the class name so python doesn't need it defined/imported yet
                #back_populates values are crossed pair, 
                    #names the other class (WorkoutLogExercise) attribute

    exercises: Mapped[list["WorkoutLogExercise"]] = relationship(

        #the matching attribute name on the other class, keeps both sides in sync
        back_populates="workout_log",

        #delete the workout = delete its exercise rows too, no orphan rows left behind
        cascade="all, delete-orphan",

        #always hand them back in the order the user entered them
        order_by="WorkoutLogExercise.exercise_order",
    )