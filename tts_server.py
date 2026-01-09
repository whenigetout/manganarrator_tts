from fastapi import FastAPI, Request, Body
from fastapi.responses import JSONResponse
from app.models.domain.exceptions import TTSInputError
from contextlib import asynccontextmanager
from app.tts_runner import TTSRunner
from app.config import TTSConfig
from fastapi.middleware.cors import CORSMiddleware
from app.models.api import TTSInput, TTSOutput, EmotionOptionsOutput
from typing import List, Any
from fastapi.exceptions import RequestValidationError
import logging
from pydantic import ValidationError
from fastapi import HTTPException

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context Manager for application lifespan.
    Code before 'yield' runs on startup.
    Code after 'yield' runs on shutdown.
    """
    # print("Application startup: Initializing resources...")
    app.state.config = TTSConfig()
    app.state.runner = TTSRunner(app.state.config)
    yield  # The application starts serving requests here
    # print("Application shutdown: Cleaning up resources...")
    # # Clean up resources
    # print("Resources cleaned up.")

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    logging.error("VALIDATION ERROR")
    logging.error(exc.errors())      # 👈 exact failing fields
    logging.error(exc.body)          # 👈 raw request body

    return JSONResponse(
        status_code=422,
        content={
            "error": "REQUEST_VALIDATION_FAILED",
            "details": exc.errors(),
        },
    )


@app.exception_handler(TTSInputError)
async def tts_input_error_handler(
    request: Request,
    exc: TTSInputError
):
    return JSONResponse(
        status_code=422,
        content={
            "error": "TTS_INPUT_ERROR",
            "message": str(exc)
        }
    )

@app.post(
    "/tts/dialogue", 
    response_model=TTSOutput,
    summary="Generate TTS for one dialogue with versioned path"
    )
def tts_dialogue(request: Request, ttsInput: TTSInput):
    try:
        # try:
        #     ttsInput = TTSInput.model_validate(ttsInput)
        # except ValidationError as e:
        #     breakpoint()  # 👈 THIS WILL FINALLY HIT
        #     raise HTTPException(
        #         status_code=422,
        #         detail={
        #             "error": "REQUEST_VALIDATION_FAILED",
        #             "details": e.errors(),
        #         },
        #     )
        runner: TTSRunner =  request.app.state.runner
        return runner.generate_line(ttsInput)
    except Exception as e:
        raise e

@app.get(
    "/tts/emotions",
    response_model=EmotionOptionsOutput,
    summary="Generate all valid Emotions list to populate DDL"
)
def tts_emotions():
    from app.models.domain.emotion import EMOTIONS
    return EmotionOptionsOutput(
        emotionOptions=sorted(
            [emotion for emotion in EMOTIONS.values()],
            key=lambda emo: emo.name)
    )
