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
        "soft": Speaker(name="soft", wav_file="rote_soft.wav", gender=GENDERS["female"]),
        "dominant": Speaker(name="dominant", wav_file="rote_loud.wav", gender=GENDERS["female"]),
        "shelby": Speaker(name="shelby", wav_file="female_shelby.wav", gender=GENDERS["female"]),
        "rote_loud": Speaker(name="rote_loud", wav_file="rote_loud.wav", gender=GENDERS["female"]),
        "rote_soft": Speaker(name="rote_soft", wav_file="rote_soft.wav", gender=GENDERS["female"]),
        "rote_very_soft": Speaker(name="rote_very_soft", wav_file="rote_very_soft.wav", gender=GENDERS["female"]),
    },
    "male": {
        "default": Speaker(name="default", wav_file="male_default.wav", gender=GENDERS["male"]),
    },
    "unknown": {
        "default": Speaker(name="default", wav_file="unknown_default.wav", gender=GENDERS["neutral"]),
    },
}

DEFAULT_GROUP: Final[str] = "unknown"
DEFAULT_SPEAKER: Final[str] = "default"
