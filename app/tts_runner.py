from pathlib import Path
from app.config import TTSConfig
from app.utils import Timer
from app.backends.chatterbox_backend import ChatterboxTTSBackend
from datetime import datetime
import uuid
import json

class TTSRunner:
    def __init__(self, config: TTSConfig):
        """
        Initialize the TTSRunner with a config and prepare the Chatterbox backend.
        """
        self.config = config
        self.output_dir = Path(config.output_folder)
        self.backend = None
        """
        Load the ChatterboxTTS model.
        """
        with Timer("🔊 Load TTS model"):
            self.backend = ChatterboxTTSBackend(self.config)

    def generate_line(
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
    ) -> dict:

        """
        Generate a TTS audio file from a single line of text and return output metadata.
        """
        if self.backend is None:
            raise RuntimeError("TTS model is not loaded.")

        wav_path = self.backend.synthesize(
            text=text,
            gender=gender,
            emotion=emotion,
            speaker_id=speaker_id,
            run_id=run_id,
            custom_filename=custom_filename,
            custom_cfg=custom_cfg,
            custom_exaggeration=custom_exaggeration,
            image_rel_path_from_root=image_rel_path_from_root,
            image_file_name=image_file_name,
            dialogue_id=dialogue_id
        )

        return {
            "text": text,
            "gender": gender,
            "emotion": emotion,
            "speaker_id": speaker_id,
            "audio_path": wav_path
        }

    def process_ocr_result(self, ocr_json: dict, ocr_runid: str) -> dict:
        """
        Process OCR output, generate voice files, and return updated JSON.
        """
        if self.backend is None:
            raise RuntimeError("TTS model is not loaded.")

        # Generate a timestamped run ID like: tts_20250730_031021_<uuid>_<ocr_runid>
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Output folder
        out_dir = self.output_dir / ocr_runid

        if not out_dir or not out_dir.is_dir():
            raise ValueError("Output folder does not exist. Did you move the folder generated from OCR-module?")

        # Begin processing
        with Timer("🔁 TTS batch generation"):
            for entry in ocr_json:
                image_name = entry.get("image", "unknown_img")

                if "parsed_dialogue" not in entry or not entry["parsed_dialogue"]:
                    print(f"⚠️ No parsed_dialogue in {image_name}")
                    continue

                for line in entry["parsed_dialogue"]:
                    text = line.get("text")
                    image_rel_path_from_root = line.get("image_rel_path_from_root")
                    image_file_name = line.get("image_file_name")
                    gender = line.get("gender", "unknown")
                    emotion = line.get("emotion", self.config.default_emotion)
                    speaker_id = line.get("speaker", "default")
                    dialogue_id = line.get("id")

                    try:
                        # file_base = f"{image_name}_dialogueid_{dialogue_id}"
                        wav_result = self.generate_line(
                            text=text,
                            gender=gender,
                            emotion=emotion,
                            speaker_id=speaker_id,
                            run_id=ocr_runid,
                            image_rel_path_from_root=image_rel_path_from_root,
                            image_file_name=image_file_name,
                            dialogue_id=dialogue_id
                        )
                        line["voice_path"] = wav_result["audio_path"]

                    except Exception as e:
                        print(f"❌ Failed to synthesize line {dialogue_id} in {image_name}: {e}")
                        line["voice_path"] = None

        # Save full updated JSON
        output_json_path = out_dir / "tts_output.json"
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(ocr_json, f, indent=2)

        return {
            "runid": ocr_runid,
            "output_folder": str(out_dir),
            "num_images": len(ocr_json)
        }
