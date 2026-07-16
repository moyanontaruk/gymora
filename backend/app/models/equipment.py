from app.database import Base
from sqlalchemy import Text, String
from sqlalchemy.orm import Mapped, mapped_column

class Equipment(Base):
    __table__ = "equipment"

    equipment_id: Mapped[int] = mapped_column(primary_key= True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable= True)

    