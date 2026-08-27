from sqlalchemy import String,ForeignKey,DateTime,func
from datetime import datetime,timezone
from sqlalchemy.orm import Mapped,mapped_column,relationship
from database import Base

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__="users"

    id:Mapped[str]=mapped_column(
        String,
        primary_key=True
        
    )
    email:Mapped[str]=mapped_column(
        String,
        index=True,
        unique=True,
        nullable=False
        
    )

    password: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    created_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False
    )
    tasks:Mapped[list["Task"]]=relationship(
        back_populates="user"
    )


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True
    )

    title: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    created_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False 
    )

    updated_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )
    user:Mapped["User"]=relationship(
        back_populates="tasks"
    )