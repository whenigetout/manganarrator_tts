@echo off
REM Activate your TTS environment and run the FastAPI server

REM Change this to your Conda environment name
CALL conda activate chatterbox

REM Run the FastAPI app using uvicorn
uvicorn tts_server:app --host 0.0.0.0 --port 7861 --reload
