from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
            primary_key=True,
            autoincrement=True
    )

    username: Mapped[str] = mapped_column(
            String(16),
            unique=True
    )
    
    password_hash: Mapped[str] = mapped_column(
            String(255)
    )

    events: Mapped[list["Event"]] = relationship(
            back_populates="owner"
    )


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    owner_id: Mapped[int] = mapped_column(
            ForeignKey("users.id")
    )

    title: Mapped[str] = mapped_column(
        String(67)
    )

    icon: Mapped[str] = mapped_column(
            String(32)
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

    visibility: Mapped[str] = mapped_column(
        String(20),
        default="private"
    )

    owner: Mapped["User"] = relationship(
        back_populates="events"
    )
