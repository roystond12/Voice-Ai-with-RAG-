import logging
import os
from typing import Annotated

from fastapi import APIRouter, HTTPException, UploadFile, File, status
from starlette.concurrency import run_in_threadpool

from tts import deepgram_client

logger = logging.getLogger(__name__)

stt_router = APIRouter()
default_stt_model: str = os.environ.get("DEFAULT_STT_MODEL", "nova-3")


def _transcribe(audio_bytes: bytes, model: str) -> str:
    """Blocking Deepgram call, meant to run in a worker thread so it doesn't
    block the event loop."""
    response = deepgram_client.listen.v1.media.transcribe_file(
        request=audio_bytes,
        model=model,
        smart_format=True,
        punctuate=True,
    )
    channels = getattr(response.results, "channels", [])
    if not channels or not channels[0].alternatives:
        return ""
    return channels[0].alternatives[0].transcript.strip()


@stt_router.post("/api/speech_to_text")
async def speech_to_text(
    audio: Annotated[UploadFile, File()],
    model: Annotated[str, "Deepgram STT model"] = default_stt_model,
):
    """
    Input -> An uploaded audio clip (multipart/form-data field "audio")
    Output -> Transcribed text (str)
    This API is used for voice-input: converts a recorded question into text
    before it's sent to /api/get_context.
    """
    try:
        audio_bytes = await audio.read()
        if not audio_bytes:
            logger.error("the audio cannot be empty")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="please provide an audio clip",
            )

        transcript = await run_in_threadpool(_transcribe, audio_bytes, model)
        return transcript

    except HTTPException:
        raise
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Speech-to-text transcription failed",
        )
