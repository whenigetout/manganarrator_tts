# domain/emotion.py
from pydantic import BaseModel, ConfigDict
from typing import Final
from app.models.domain.emotion_params import EmotionParams

class Emotion(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    params: EmotionParams


EMOTIONS: Final[dict[str, Emotion]] = {
    "neutral": Emotion(
        name="neutral",
        params=EmotionParams(cfg=0.5, exaggeration=0.5),
    ),
    "calm": Emotion(
        name="calm",
        params=EmotionParams(cfg=0.45, exaggeration=0.4),
    ),
    "happy": Emotion(
        name="happy",
        params=EmotionParams(cfg=0.65, exaggeration=0.7),
    ),
    "sad": Emotion(
        name="sad",
        params=EmotionParams(cfg=0.55, exaggeration=0.6),
    ),
    "angry": Emotion(
        name="angry",
        params=EmotionParams(cfg=0.75, exaggeration=0.85),
    ),
}

DEFAULT_EMOTION: Final[str] = "neutral"
