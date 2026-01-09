from pydantic import BaseModel, Field, ConfigDict, field_validator
from enum import Enum
from typing import Optional, Literal, Final
from pathlib import Path
from app.models.domain import (
    emotion as e,
    gender as g,
    speaker as s,
    emotion_params as ep
)
from mn_contracts import ocr as o

class TTSInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    text: str
    gender: g.Gender
    emotion: e.Emotion
    speaker: s.Speaker
    image_ref: o.MediaRef
    customSettings: Optional[ep.EmotionParams] = None
    run_id: str = ""
    custom_filename: str = ""
    dialogue_id: int = -1

