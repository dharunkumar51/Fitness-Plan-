from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
    select,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    sessionmaker,
)


# ---------------------------------------------------------
# Environment
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./fitbuddy.db",
)


# ---------------------------------------------------------
# Database engine
# ---------------------------------------------------------

connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False


engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    future=True,
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


# ---------------------------------------------------------
# Base model
# ---------------------------------------------------------

class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------
# User table
# ---------------------------------------------------------

class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )

    username: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    age: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    weight: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    goal: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    intensity: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    plans: Mapped[list["Plan"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="Plan.id.desc()",
    )


# ---------------------------------------------------------
# Plan table
# ---------------------------------------------------------

class Plan(Base):

    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey(
            "users.user_id",
            ondelete="CASCADE",
        ),
        index=True,
        nullable=False,
    )

    original_plan: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    updated_plan: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    nutrition_tip: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    feedback: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )

    user: Mapped["User"] = relationship(
        back_populates="plans",
    )


# ---------------------------------------------------------
# Initialize database
# ---------------------------------------------------------

def init_db() -> None:

    Base.metadata.create_all(
        bind=engine,
    )


# ---------------------------------------------------------
# Save / update user
# ---------------------------------------------------------

def save_user(data: dict) -> User:

    init_db()

    with SessionLocal() as db:

        existing_user = db.scalar(
            select(User).where(
                User.user_id == data["user_id"]
            )
        )

        if existing_user:

            existing_user.username = data["username"]
            existing_user.age = data["age"]
            existing_user.weight = data["weight"]
            existing_user.goal = data["goal"]
            existing_user.intensity = data["intensity"]

            db.commit()
            db.refresh(existing_user)

            return existing_user

        user = User(
            **data
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user


# ---------------------------------------------------------
# Save plan
# ---------------------------------------------------------

def save_plan(
    user_id: str,
    original_plan: str,
    nutrition_tip: str,
) -> Plan:

    with SessionLocal() as db:

        plan = Plan(
            user_id=user_id,
            original_plan=original_plan,
            nutrition_tip=nutrition_tip,
        )

        db.add(plan)

        db.commit()
        db.refresh(plan)

        return plan


# ---------------------------------------------------------
# Update plan
# ---------------------------------------------------------

def update_plan(
    plan_id: int,
    updated_plan: str,
    feedback: str,
    nutrition_tip: str,
) -> Optional[Plan]:

    with SessionLocal() as db:

        plan = db.get(
            Plan,
            plan_id,
        )

        if plan is None:
            return None

        plan.updated_plan = updated_plan
        plan.feedback = feedback
        plan.nutrition_tip = nutrition_tip
        plan.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(plan)

        return plan


# ---------------------------------------------------------
# Get user
# ---------------------------------------------------------

def get_user(
    user_id: str,
) -> Optional[User]:

    init_db()

    with SessionLocal() as db:

        return db.scalar(
            select(User).where(
                User.user_id == user_id
            )
        )


# ---------------------------------------------------------
# Get latest plan
# ---------------------------------------------------------

def get_latest_plan(
    user_id: str,
) -> Optional[Plan]:

    init_db()

    with SessionLocal() as db:

        return db.scalar(
            select(Plan)
            .where(
                Plan.user_id == user_id
            )
            .order_by(
                Plan.id.desc()
            )
        )


# ---------------------------------------------------------
# Get all users
# ---------------------------------------------------------

def get_all_users() -> list[User]:

    init_db()

    with SessionLocal() as db:

        return list(
            db.scalars(
                select(User)
                .order_by(
                    User.id.desc()
                )
            ).all()
        )


# ---------------------------------------------------------
# Get users and latest plans
# ---------------------------------------------------------

def get_all_users_with_plans():

    users = get_all_users()

    result = []

    for user in users:

        plan = get_latest_plan(
            user.user_id
        )

        result.append(
            (
                user,
                plan,
            )
        )

    return result


# ---------------------------------------------------------
# Delete user
# ---------------------------------------------------------

def delete_user(
    user_id: str,
) -> bool:

    init_db()

    with SessionLocal() as db:

        user = db.scalar(
            select(User).where(
                User.user_id == user_id
            )
        )

        if user is None:
            return False

        db.delete(user)
        db.commit()

        return True