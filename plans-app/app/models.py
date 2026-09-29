from sqlalchemy import String
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    title: Mapped[str] = mapped_column(
        String(255)
    )

    description: Mapped[str] = mapped_column(
        String(1000)
    )

    start_at: Mapped[str] = mapped_column(
        DateTime
    )

    end_at: Mapped[str] = mapped_column(
        DateTime
    )
