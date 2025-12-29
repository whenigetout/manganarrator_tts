from fastapi import FastAPI, HTTPException, UploadFile, File
from app.tts_runner import TTSRunner
from app.config import TTSConfig
import json
from pathlib import Path
from pydantic import BaseModel, Field
from enum import Enum
from uuid import uuid4
from app.utils import Timer
from fastapi.middleware.cors import CORSMiddleware
import os



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = TTSConfig()
runner = TTSRunner(config)

from typing import Optional, Union
from fastapi import Body

@app.post("/tts/from_ocr_json")
async def run_tts_from_ocr_json(
    file: Optional[UploadFile] = File(None),
    file_path: Optional[str] = Body(None),
    ocr_runid: str = Body(...)
):
    """
    Accepts an OCR pretty JSON (either via Upload or path) + run ID, returns TTS batch result.
    """
    if not ocr_runid:
        raise HTTPException(status_code=400, detail="Missing ocr_runid")

    if file:
        try:
            contents = await file.read()
            ocr_data = json.loads(contents)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid uploaded JSON: {e}")
    elif file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                ocr_data = json.load(f)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not load file from path: {e}")
    else:
        raise HTTPException(status_code=400, detail="You must provide either a file upload or a file path.")

    try:
        result = runner.process_ocr_result(ocr_data, ocr_runid)
        return result
    except Exception as e:
        from app.utils import log_exception
        log_exception("Failed generating TTS in run_tts_from_ocr_json:")
        raise HTTPException(status_code=500, detail=f"TTS failed: {e}")


@app.get("/tts/result/{tts_runid}")
def get_tts_result(tts_runid: str):
    """
    Fetch the final tts_output.json for a previous run.
    """
    out_path = Path(config.output_folder) / tts_runid / "tts_output.json"

    if not out_path.exists():
        raise HTTPException(status_code=404, detail="Run ID not found")

    with open(out_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data

from pydantic import BaseModel, Field

class LineRequest(BaseModel):
    text: str = Field(..., example="I'll protect you.")
    gender: str = Field(..., example="female")         # Options: male, female, unknown
    emotion: str = Field(..., example="calm")          # Your emotion key (as per emotion map)
    speaker_id: str = Field(..., example="female_generic")  # Any valid voice reference name

@app.post("/tts/line", summary="Tts Single Line")
async def tts_single_line(request: LineRequest):
    try:
        audio_path = runner.generate_line(
            text=request.text,
            gender=request.gender,
            emotion=request.emotion,
            speaker_id=request.speaker_id
        )
        return {"status": "success", "audio_path": str(audio_path)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

from typing import Optional

class EmotionTuneRequest(BaseModel):
    text: str = Field(..., example="I thought I could trust you… but now, I don’t even know who you are anymore.")
    gender: str = Field(..., example="female")
    emotion: Optional[str] = Field(default=None, example="neutral")
    speaker_id: str = Field(..., example="default")
    exaggeration: Optional[float] = Field(default=None, example=0.5)
    cfg: Optional[float] = Field(default=None, example=0.5)


@app.post("/tts/tune_emotion", summary="TTS Emotion Tuning")
async def tts_emotion_tuning(request: EmotionTuneRequest):
    """
    Manually tune exaggeration and cfg for a specific voice (no emotion mapping or gender).
    """
    try:
        from datetime import datetime
        from uuid import uuid4

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid4().hex[:6]

        filename = f"{request.speaker_id}_{timestamp}_exg{request.exaggeration}_cfg{request.cfg}_{unique_id}"

        audio_path = runner.generate_line(
            text=request.text,
            gender=request.gender,
            emotion=request.emotion,
            speaker_id=request.speaker_id,
            run_id="emotion_tuning",
            custom_filename=filename,
            custom_cfg=request.cfg,
            custom_exaggeration=request.exaggeration
        )

        return {"status": "success", "audio_path": str(audio_path)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

class TTSDialogueRequest(BaseModel):
    text: str
    gender: str
    emotion: str
    speaker_id: str
    run_id: str
    image_rel_path_from_root: str
    image_file_name: str
    dialogue_id: int
    use_custom_params: bool = False
    exaggeration: Optional[float] = None
    cfg: Optional[float] = None

class TTSDialogueResponse(BaseModel):
    status: str
    audio_path: str


@app.post(
    "/tts/dialogue", 
    response_model=TTSDialogueResponse,
    summary="Generate TTS for one dialogue with versioned path"
    )
def tts_dialogue(request: TTSDialogueRequest):
    try:

        filename = os.path.basename(request.image_file_name)  # removes all preceding folders
        sanitized_filename = filename.replace(".", "_")       # replaces '.' in extension
        base_dir = Path(runner.config.output_folder).resolve()

        kwargs = {
            "text": request.text,
            "gender": request.gender,
            "emotion": request.emotion,
            "speaker_id": request.speaker_id,
            "run_id": request.run_id,
            "image_rel_path_from_root": request.image_rel_path_from_root,
            "image_file_name": sanitized_filename,  # 👈 fix applied here
            "dialogue_id": request.dialogue_id,
        }

        if request.use_custom_params:
            kwargs["custom_cfg"] = request.cfg
            kwargs["custom_exaggeration"] = request.exaggeration

        result = runner.generate_line(**kwargs)
        abs_path = Path(result["audio_path"]).resolve()
        rel_path = abs_path.relative_to(base_dir)

        return TTSDialogueResponse(
            status= "success",
            audio_path= rel_path.as_posix()
        )

    except Exception as e:
        from app.utils import log_exception
        log_exception("Failed TTS for dialogue line:")

        raise HTTPException(
            status_code=500,
            detail={
                "error": "TTS_FAILED",
                "message": str(e),
                "run_id": request.run_id,
                "dialogue_id": request.dialogue_id
            }
        )


