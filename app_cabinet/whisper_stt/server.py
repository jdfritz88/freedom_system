"""
Whisper STT Server - OpenAI-compatible Speech-to-Text API
Uses faster-whisper for GPU-accelerated transcription.
Runs on port 8787.
"""
import io
import logging
from pathlib import Path

import numpy as np
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse
import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format="[WHISPER_STT] [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("F:/Apps/freedom_system/log/whisper_stt.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Freedom Whisper STT", version="1.0.0")

# Global model reference
_model = None
MODEL_SIZE = "base.en"


def get_model():
    """Lazy-load the faster-whisper model on first request."""
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        logger.info(f"Loading faster-whisper model '{MODEL_SIZE}'...")
        _model = WhisperModel(MODEL_SIZE, device="cuda", compute_type="float16")
        logger.info("Model loaded successfully.")
    return _model


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ready", "model": MODEL_SIZE}


@app.get("/v1/models")
async def list_models():
    """List available models (OpenAI-compatible)."""
    return {
        "object": "list",
        "data": [{"id": "whisper-1", "object": "model", "owned_by": "local"}],
    }


@app.post("/v1/audio/transcriptions")
async def transcribe(
    file: UploadFile = File(...),
    model: str = Form(default="whisper-1"),
    language: str = Form(default="en"),
    response_format: str = Form(default="json"),
    temperature: float = Form(default=0.0),
):
    """
    OpenAI-compatible transcription endpoint.
    Accepts audio file, returns transcribed text.
    """
    try:
        audio_bytes = await file.read()
        logger.info(f"Received audio: {len(audio_bytes)} bytes, format: {file.content_type}")

        # Decode audio to numpy array using av
        import av
        container = av.open(io.BytesIO(audio_bytes))
        audio_stream = next(s for s in container.streams if s.type == "audio")

        frames = []
        resampler = av.AudioResampler(format="s16", layout="mono", rate=16000)
        for frame in container.decode(audio_stream):
            resampled = resampler.resample(frame)
            for r in resampled:
                arr = r.to_ndarray().flatten()
                frames.append(arr)

        if not frames:
            return JSONResponse(
                status_code=400,
                content={"error": "No audio frames decoded"},
            )

        audio_array = np.concatenate(frames).astype(np.float32) / 32768.0

        whisper_model = get_model()
        segments, info = whisper_model.transcribe(
            audio_array,
            language=language if language != "auto" else None,
            temperature=temperature,
            vad_filter=True,
        )

        text = " ".join(segment.text.strip() for segment in segments)
        logger.info(f"Transcribed: '{text[:100]}...' (lang={info.language}, prob={info.language_probability:.2f})")

        if response_format == "text":
            return text

        return {
            "text": text,
            "language": info.language,
            "duration": info.duration,
        }

    except Exception as e:
        logger.error(f"Transcription failed: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )


if __name__ == "__main__":
    logger.info("Starting Whisper STT server on port 8787...")
    get_model()  # Pre-load model at startup
    uvicorn.run(app, host="127.0.0.1", port=8787, log_level="info")
