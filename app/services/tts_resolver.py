# services/tts_resolver.py
from app.models.domain.emotion import Emotion, EMOTIONS, DEFAULT_EMOTION
from app.models.domain.speaker import Speaker, SPEAKER_GROUPS, DEFAULT_GROUP, DEFAULT_SPEAKER
from app.models.domain.gender import Gender, GENDERS, DEFAULT_GENDER
from app.models.domain.emotion_params import EmotionParams
from typing import Optional

def resolve_emotion(
    emotion_name: str | None,
    customSettings: Optional[EmotionParams] = None
) -> Emotion:
    base = EMOTIONS.get(
        (emotion_name or DEFAULT_EMOTION).lower(),
        EMOTIONS[DEFAULT_EMOTION],
    )

    if not customSettings:
        return base

    return Emotion(
        name=base.name,
        params=customSettings,
    )


def resolve_speaker(
    gender: Gender,
    speaker: Optional[Speaker] = None,
) -> Speaker:
    speaker_group = SPEAKER_GROUPS.get(
        gender.value,
        SPEAKER_GROUPS[DEFAULT_GROUP],
    )

    if not speaker or speaker.name not in speaker_group:
        return speaker_group[DEFAULT_SPEAKER]

    return speaker_group[speaker.name]


def resolve_gender(gender: str | None) -> Gender:
    return GENDERS.get(
        (gender or DEFAULT_GENDER).lower(),
        GENDERS[DEFAULT_GENDER],
    )
