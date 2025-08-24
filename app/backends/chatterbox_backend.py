import uuid
from pathlib import Path
import torch
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS
from app.utils import ensure_folder, Timer

class ChatterboxTTSBackend:
    def __init__(self, config):
        self.config = config
        self.model = self._load_model()

    def _load_model(self):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🧠 Loading Chatterbox model on: {device}")
        return ChatterboxTTS.from_pretrained(device=device)

    def synthesize(
        self,
        text: str,
        gender: str,
        emotion: str = None,
        speaker_id: str = "default",
        run_id: str = None,
        custom_filename: str = None,
        custom_cfg: float = None,
        custom_exaggeration: float = None,
        image_rel_path_from_root: str = None,
        image_file_name: str = None,
        dialogue_id: str = None
    ) -> str:
        """
        Generate speech from text using ChatterboxTTS.
        Returns path to generated .wav file.
        """
        gender = gender.lower() if gender else "unknown"
        emotion = emotion.lower() if emotion else self.config.default_emotion
        speaker_id = speaker_id or "default"

        # For female voice "RoteDisaster" from gonewildaudio these settings work better and it is not possible to express
        # all said emotions with just one sample voice files so we divide voice samples to be used based on emotions
        # this has been curated and tested, only for this voice at the time of writing (Fri, 01 Aug, 2025)
        if gender == "female": # and speaker_id in ["rote_loud", "rote_very_soft", "default"]:
            if emotion in ['neutral', 'happy', 'angry', 'surprised', 'excited', 'scared', 'curious', 'playful', 'serious']:
                speaker_id = "rote_loud"
            elif emotion in ['sad', 'nervous', 'aroused', 'calm']:
                speaker_id = "rote_very_soft"
            else:
                speaker_id = "default"
        else:
            speaker_id = "default"

        voice_ref_path = self._get_voice_ref(gender, speaker_id)
        if custom_cfg is not None and custom_exaggeration is not None:
            cfg = custom_cfg
            exaggeration = custom_exaggeration
        else:
            cfg, exaggeration = self._get_emotion_settings(speaker_id, emotion)

        subfolder = "tts_run"
        output_dir = self.config.output_folder / subfolder if not run_id else self.config.output_folder / run_id / image_rel_path_from_root
        ensure_folder(output_dir)

        from collections import defaultdict

        # Helper to extract version number by checking existing files
        def get_next_version(folder: Path) -> int:
            pattern = f"v*.wav"
            versions = []
            for file in folder.glob(pattern):
                parts = file.stem.split("__")
                if len(parts) > 0 and parts[0].startswith("v"):
                    try:
                        version_num = int(parts[0][1:])
                        versions.append(version_num)
                    except ValueError:
                        continue
            return max(versions, default=0) + 1


        # If custom filename is provided
        if custom_filename:
            filename = f"{custom_filename}.wav"
            out_path = output_dir / filename

        # If no run_id, fallback to timestamp-based name
        elif not run_id:
            from datetime import datetime
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{image_file_name}__{ts}.wav"
            out_path = output_dir / filename

        # For normal batch generation using run_id
        else:
            assert image_file_name is not None, "Missing image_file_name in batch mode"
            assert image_rel_path_from_root is not None, "Missing image_rel_path_from_root in batch mode"
            assert dialogue_id is not None, "Missing dialogue_id for batch TTS output naming"
            dialogue_id = int(dialogue_id)

            # Convert img1.jpg → img1_jpg
            img_base = Path(image_file_name).stem.replace('.', '_')
            dialogue_subfolder = (
                output_dir / f"{img_base}" / f"dialogue__{dialogue_id}"
            )
            ensure_folder(dialogue_subfolder)

            version = get_next_version(dialogue_subfolder)
            filename = f"v{version}__exg{exaggeration}__cfg{cfg}.wav"
            out_path = dialogue_subfolder / filename

        with Timer(f"🔊 Synthesizing audio with voice: {voice_ref_path.name} emotion:{emotion}, exg:{exaggeration}, cfg:{cfg}", use_spinner=False):
            wav = self.model.generate(
                text,
                audio_prompt_path=str(voice_ref_path),
                exaggeration=exaggeration,
                cfg_weight=cfg
            )
            ta.save(str(out_path), wav, self.model.sr)

        return str(out_path)

    def _get_voice_ref(self, gender: str, speaker_id: str) -> Path:
        speaker_group = self.config.speaker_map.get(gender, {})
        if not speaker_group.get(speaker_id):
            print(f"⚠️ Invalid speaker_id: {speaker_id}. Using default voice.")
        voice_ref = speaker_group.get(speaker_id) or speaker_group.get("default")
        if not voice_ref:
            raise ValueError(f"No voice reference for gender '{gender}' and speaker_id '{speaker_id}'")
        return self.config.voice_ref_dir / voice_ref

    def _get_emotion_settings(self, voice_key: str, emotion: str) -> tuple:
        emotion_cfg = self.config.emotion_map.get(voice_key, {}).get(emotion)

        if emotion_cfg is None:
            print(f"⚠️ No emotion settings for voice '{voice_key}' and emotion '{emotion}', using defaults.")
            return self.config.default_cfg, self.config.default_exaggeration

        cfg = emotion_cfg.get("cfg", self.config.default_cfg)
        exaggeration = emotion_cfg.get("exaggeration", self.config.default_exaggeration)
        print(f"🌿ℹ Using predefinted values for voice {voice_key} - exg: {exaggeration} cfg: {cfg}")
        return cfg, exaggeration
