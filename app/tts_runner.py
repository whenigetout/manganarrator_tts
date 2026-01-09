from pathlib import Path
from app.config import TTSConfig
from app.utils import Timer
from app.backends.chatterbox_backend import ChatterboxTTSBackend
from app.models.domain import (
    domain as d, 
    exceptions as ex,
    speaker as s
)
from app.models.api import TTSOutput
from app.services.tts_resolver import (
    resolve_emotion,
    resolve_gender,
    resolve_speaker
)
from app.utils import ensure_folder

class TTSRunner:
    def __init__(self, config: TTSConfig):
        """
        Initialize the TTSRunner with a config and prepare the Chatterbox backend.
        """
        self.config = config
        self.media_root = str(config.media_root)
        self.media_namespace = str(config.media_namespace)
        self.backend = None
        """
        Load the ChatterboxTTS model.
        """
        with Timer("🔊 Load TTS model"):
            self.backend = ChatterboxTTSBackend(self.config)

    def generate_line(
        self,
        req: d.TTSInput
    ) -> TTSOutput:

        """
        Generate a TTS audio file from a single line of text and return output metadata.
        """
        try:
            if self.backend is None:
                raise RuntimeError("TTS model is not loaded.")
            
            gender = resolve_gender(req.gender.value)
            emotion = resolve_emotion(req.emotion.name, req.customSettings)
            

            # Remove this later after tuning voices -----------------
                # For female voice "RoteDisaster" from gonewildaudio these settings work better and it is not possible to express
                # all said emotions with just one sample voice files so we divide voice samples to be used based on emotions
                # this has been curated and tested, only for this voice at the time of writing (Fri, 01 Aug, 2025)
            speaker_name = ""
            if gender.value == "female": # and speaker in ["rote_loud", "rote_very_soft", "default"]:
                if emotion.name in ['neutral', 'happy', 'angry', 'surprised', 'excited', 'scared', 'curious', 'playful', 'serious']:
                    speaker_name = "rote_loud"
                elif emotion.name in ['sad', 'nervous', 'aroused', 'calm']:
                    speaker_name = "rote_very_soft"
                else:
                    speaker_name = "default"
            else:
                pass


            speaker = resolve_speaker(req.gender, req.speaker if not speaker_name else 
                                      s.Speaker(
                                          name=speaker_name,
                                          wav_file="",
                                          gender=gender
                                      )
                                      )

            
            # -------------------------------------------------------

            # Prevent invalid inputs
            if not req.text or not req.run_id or req.dialogue_id < 0:
                raise ex.TTSInputError("Invalid TTS Input")

            new_req = req.model_copy(
                update={
                    "gender": gender,
                    "emotion": emotion,
                    "speaker": speaker
                }
            )

            # if the img name is "img002.jpg", then out_dir = "image002_jpg"
            root = self.media_root
            ns = self.media_namespace
            img_path_without_ext = Path(req.image_ref.path).with_suffix("")
            img_ext_without_dot = req.image_ref.suffix[1:] # exclude the "."
            out_dir: Path = Path(root)/ns/new_req.run_id/f"{img_path_without_ext}_{img_ext_without_dot}"
            ensure_folder(out_dir)

            res: TTSOutput = self.backend.synthesize(
                req=new_req,
                out_dir=out_dir
                )

            return res
        except Exception as e:
            raise ex.TTSInputError("Input data validation failed") from e

