# domain/speaker.py
from pydantic import BaseModel, ConfigDict
from typing import Final
from app.models.domain.gender import Gender, GENDERS, DEFAULT_GENDER

class Speaker(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    wav_file: str
    gender: Gender

SPEAKER_GROUPS: Final[dict[str, dict[str, Speaker]]] = {
    "female": {
        "default": Speaker(name="default", wav_file="female_default.wav", gender=GENDERS["female"]),
        "soft": Speaker(name="soft", wav_file="female_soft.wav", gender=GENDERS["female"]),
        "dominant": Speaker(name="dominant", wav_file="female_dom.wav", gender=GENDERS["female"]),
    },
    "male": {
        "default": Speaker(name="default", wav_file="male_default.wav", gender=GENDERS["male"]),
    },
    "unknown": {
        "default": Speaker(name="default", wav_file="neutral.wav", gender=GENDERS[DEFAULT_GENDER]),
    },
}

DEFAULT_GROUP: Final[str] = "unknown"
DEFAULT_SPEAKER: Final[str] = "default"
