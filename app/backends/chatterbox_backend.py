from pathlib import Path
import torch
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS
from app.utils import ensure_folder, Timer, get_next_version
from app.models.domain import (
    domain as d,
    emotion_params as ep,
    exceptions as ex
)
from app.models.api import TTSOutput
from app.config import TTSConfig

class ChatterboxTTSBackend:
    def __init__(self, config: TTSConfig):
        self.config = config
        self.model = self._load_model()

    def _load_model(self):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🧠 Loading Chatterbox model on: {device}")
        return ChatterboxTTS.from_pretrained(device=device)

    def synthesize(
        self,
        req: d.TTSInput,
        out_dir: Path
    ) -> TTSOutput:
        """
        Generate speech from text using ChatterboxTTS.
        Returns path to generated .wav file.
        """
        
        # For normal batch generation using run_id ie when input comes through the api endpoint
        try:

            dialogue_subfolder: Path = (
                out_dir / f"dialogue__{req.dialogue_id}"
            ).resolve()
            dialogue_subfolder = ensure_folder(dialogue_subfolder)

            version: int = get_next_version(dialogue_subfolder)
            emotion_params: ep.EmotionParams = req.emotion.params
            filename: str = f"v{version}__exg{emotion_params.exaggeration}__cfg{emotion_params.cfg}.wav"
            out_path: Path = dialogue_subfolder / filename

            with Timer(f"🔊 Synthesizing audio with voice: {req.speaker.name} emotion:{req.emotion.name}, exg:{emotion_params.exaggeration}, cfg:{emotion_params.cfg}", use_spinner=False):
                wav = self.model.generate(
                    req.text,
                    audio_prompt_path=str(Path(self.config.voice_ref_dir)/req.speaker.wav_file),
                    exaggeration=emotion_params.exaggeration,
                    cfg_weight=emotion_params.cfg
                )
                ta.save(str(out_path), wav, self.model.sr)
                print(f"IN synthesize(): saved wav file at {str(out_path)}")

            return TTSOutput(
                ttsInput=req,
                audio_ref=d.MediaRef(
                    namespace=d.MediaNamespace.OUTPUTS,
                    path=(out_path.relative_to(Path(self.config.media_root)/self.config.media_namespace)).as_posix()
                )
            )
        except Exception as e:
            raise ex.TTSSynthesisError from e
