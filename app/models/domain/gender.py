# domain/gender.py
from pydantic import BaseModel, ConfigDict
from typing import Final, Literal


class Gender(BaseModel):
    model_config = ConfigDict(frozen=True)

    value: Literal["female", "male", "neutral"]

GENDERS: Final[dict[str, Gender]] = {
    "female": Gender(value="female"),
    "male": Gender(value="male"),
    "neutral": Gender(value="neutral"),
}

DEFAULT_GENDER: Final[str] = "neutral"

