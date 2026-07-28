from fastapi import APIRouter,Request,HTTPException,status,Response
import os
import re
import logging
from typing import Annotated

from dotenv import load_dotenv
from deepgram import DeepgramClient
from starlette.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)

def validate_api_key()->str:
    api_key:str = os.environ.get("DEEPGRAM_API_KEY",None)
    if not api_key:
        logging.error("""
                      DeepGram API Key is not provided
                      Please Ensure this things are followed
                      1. Create a .venv file
                      2. Assgin the parameters like this
                          (DEEPGRAM_API_KEY="<deep_gram_api_key>")""")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="DeepGram API Key is not provided"
        )
    return api_key


tts_router = APIRouter()
load_dotenv(override=False)
defualt_model:str = os.environ.get("DEFAULT_MODEL","aura-2-thalia-en")
config = {
    "port":int(os.environ.get("PORT",8081)),
    "host":os.environ.get("HOST","0.0.0.0")
}
deepgram_api_key:str = validate_api_key()
models_list = [
    "aura-2-thalia-en",
    "aura-2-asteria-en",
    "aura-2-luna-en",
    "aura-2-orion-en",
    "aura-2-zeus-en",
    "aura-2-hera-en",
    "aura-2-apollo-en",
    "aura-2-arcas-en",
]

deepgram_client = DeepgramClient(api_key=deepgram_api_key)


def _normalize_text_for_speech(text: str) -> str:
    cleaned = re.sub(r"[*_`#]+", "", text).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    if cleaned and cleaned[-1] not in ".!?":
        cleaned += "."
    return cleaned


def _generate_speech(text: str, model: str) -> bytes:
    audio_generator = deepgram_client.speak.v1.audio.generate(
        text=_normalize_text_for_speech(text),
        model=model,
        encoding="linear16",
        sample_rate=48000,
        container="wav",
    )
    return b"".join(audio_generator)

# @tts_router.get("/")
# def hello():
#     return "hii"

@tts_router.post("/api/text_to_speech")
async def text_to_speech(
    request:Request,
    model:Annotated[str,"Defualt Model"] = defualt_model,
    ):
    """
    Input -> Receives text input (str) in json body
    Output -> Converts str to audio bytes
    This API is used for text to speech conversion
    """
    try:
        if model not in models_list:
            logger.error(f"""
                        Select Models from the list : {"\n".join(name for name in models_list)}
                        """)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="please select proper models"
            )

        if request.headers.get("content-type","") != "application/json":
            logger.error("please provide json body")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail = "please provide the json body"
            )

        body = await request.json()
        text = body.get("text","").strip()

        if not text:
            logger.error("the text cannot be empty")
            raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                        detail = "please provide the text"
                    )

        audio_bytes = await run_in_threadpool(_generate_speech, text, model)

        return Response(
            content = audio_bytes,
            media_type="audio/wav"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code = status.HTTP_502_BAD_GATEWAY,
            detail="Text-to-speech generation failed"
        )
