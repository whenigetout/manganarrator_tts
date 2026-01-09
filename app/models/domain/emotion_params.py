# domain/emotion_params.py
from pydantic import BaseModel, Field, ConfigDict

class EmotionParams(BaseModel):
    model_config = ConfigDict(frozen=True)

    cfg: float = Field(ge=0.0)
    exaggeration: float = Field(ge=0.0)
