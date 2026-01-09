from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.models.domain.domain import TTSInput
from app.models.domain.emotion import Emotion
from mn_contracts.ocr import MediaRef

class TTSOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    ttsInput: TTSInput
    audio_ref: MediaRef

class EmotionOptionsOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    emotionOptions: list[Emotion]