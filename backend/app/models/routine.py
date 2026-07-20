from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from datetime import datetime

class Routine(Base):
    __tablename__ = "routine"

    routine_id: Mapped[int] = mapped_column(primary_key= True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable= False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    goal: Mapped[str] = mapped_column(String(100), nullable= False)
    experience_level: Mapped[str | None] = mapped_column(String(50), nullable= True)
    target_muscle_group_id: Mapped[int | None] = mapped_column(
        ForeignKey("muscle_groups.muscle_group_id"), 
        nullable= True)
    days_per_week: Mapped[int | None] = mapped_column(nullable=True)
    session_length_minutes: Mapped[int | None] = mapped_column(nullable=True)
    is_saved: Mapped[bool] =mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone= True),
        nullable=False, 
        server_default=func.now())
    updated_at: Mapped[datetime | None] =mapped_column(DateTime(timezone=True), nullable=True)
