from typing import Literal

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------
# Allowed values
# ---------------------------------------------------------

Goal = Literal[
    "weight loss",
    "muscle gain",
    "general wellness",
    "flexibility",
    "fitness",
]


Intensity = Literal[
    "low",
    "medium",
    "high",
]


# ---------------------------------------------------------
# User input
# ---------------------------------------------------------

class UserInput(BaseModel):

    username: str = Field(
        min_length=2,
        max_length=100,
    )

    user_id: str = Field(
        min_length=2,
        max_length=100,
    )

    age: int = Field(
        ge=13,
        le=100,
    )

    weight: float = Field(
        gt=20,
        lt=400,
    )

    goal: Goal

    intensity: Intensity

    @field_validator(
        "username",
        "user_id",
    )
    @classmethod
    def validate_text(cls, value: str) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "This field cannot be empty."
            )

        return value


# ---------------------------------------------------------
# Feedback
# ---------------------------------------------------------

class FeedbackRequest(BaseModel):

    user_id: str = Field(
        min_length=2,
        max_length=100,
    )

    feedback: str = Field(
        min_length=3,
        max_length=2000,
    )

    @field_validator(
        "user_id",
        "feedback",
    )
    @classmethod
    def validate_feedback(cls, value: str) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "This field cannot be empty."
            )

        return value