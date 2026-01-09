# app/config.py

import yaml
from pathlib import Path

class TTSConfig:
    def __init__(self, config_path="config.yaml"):
        try:
            self.root = Path(__file__).parent.parent
            self.config = self._load_yaml(self.root / config_path)
            
            self.media_root = self.config.get("media_root")
            self.media_namespace = self.config.get("media_namespace")
            self.voice_ref_dir = self.root / self.config.get("voice_ref_dir", "voice_refs")
            self.default_speaker = self.config.get("default_speaker", "female_generic")
            self.default_emotion = self.config.get("default_emotion", "neutral")
            self.default_cfg = self.config.get("default_cfg", 0.5)
            self.default_exaggeration = self.config.get("default_exaggeration", 0.5)
            self.use_timestamped_output = self.config.get("use_timestamped_output", True)

            # speaker & emotion maps
            self.speaker_map = self._load_yaml(self.root / "app" / "data_maps" / "speaker_map.yaml")
            self.emotion_map = self._load_yaml(self.root / "app" / "data_maps" / "emotion_map.yaml")
        except:
            raise ValueError("Error loading config.yaml")

    def _load_yaml(self, path: Path):
        if not path.exists():
            raise FileNotFoundError(f"Missing YAML config: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
