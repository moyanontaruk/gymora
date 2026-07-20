from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column
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