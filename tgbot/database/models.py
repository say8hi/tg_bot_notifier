import datetime
import enum
from typing import Annotated
from sqlalchemy import BigInteger, ForeignKey, text
from sqlalchemy.orm import Mapped, defaultload, mapped_column, relationship
from .database import Base

intpk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[
    datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))
]


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    lang: Mapped[str] = mapped_column(default="en")
    registered_at: Mapped[created_at]
    time_zone: Mapped[str] = mapped_column(default="Asia/Almaty")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE")
    )
    description: Mapped[str]
    date_completed: Mapped[str]
    title: Mapped[str]
    is_on: Mapped[int] = mapped_column(default=1)
    date_created: Mapped[created_at]


class TimeZone(Base):
    __tablename__ = "time_zones"

    id: Mapped[intpk]
    user_id: Mapped[str]
