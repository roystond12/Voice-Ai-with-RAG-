from fastapi import APIRouter,Request,HTTPException,status,Response
import os
import secrets
import time
from dotenv import load_dotenv
from deepgram import DeepgramClient
import logging
from typing import Annotated
import sys


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
    "aura-2-thalia-en"
]

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
            logging.error(f"""
                        Select Models from the list : {"\n".join(name for name in models_list)}
                        """)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="please select proper models"
            )
            
        if request.headers.get("content-type","") != "application/json":
            logging.error("please provide json body")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail = "please provide the json body"
            )
            
        body = await request.json()
        text = body.get("text","").strip()
        
        if not text:
            logging.error("the text cannot be empty") 
            raise HTTPException(
                        status_code=status.HTTP_204_NO_CONTENT,
                        detail = "please provide the text"
                    )
        client = DeepgramClient(api_key = deepgram_api_key)
        audio_generator = client.speak.v1.audio.generate(
            text = text,
            model = model
        )
        
        audio_bytes = b''.join(audio_generator)
        
        return Response(
            content = audio_bytes,
            media_type="application/octet-stream"
        )
    except Exception as e:
        logging.error(e)
        HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail="Bad Request"
        )
        

        
        

