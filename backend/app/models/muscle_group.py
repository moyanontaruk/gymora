from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

#note to self
#SQLAlchemy String(100) → PostgreSQL VARCHAR(100) → Python str
#SQLAlchemy Text        → PostgreSQL TEXT         → Python str

class MuscleGroup(Base):
    __tablename__ = "muscle_groups"
    
    muscle_group_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description :Mapped[str | None] = mapped_column(Text, nullable=True)
   