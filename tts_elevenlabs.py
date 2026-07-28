from __future__ import annotations

from dotenv import load_dotenv
import os 
from elevenlabs import AsyncElevenLabs,VoiceSettings
from pydantic import BaseModel
import logging
from fastapi import HTTPException,status
import builtins
import datetime

load_dotenv()

class GeneratedVoice(BaseModel):
    """
    Genrated Voice Result
    """
    audio_data : bytes
    filepath : str | None = None
    dialogue_index : int | None = None
    generated_at : str
    
class GeneratedVoiceResult(BaseModel):
    """Voice generation result with metadata"""

    voices: list[GeneratedVoice]
    text: str
    voice_id: str
    model: str
    cost: float | None = None
    
def validate_api_key(api_key:str|None = None)->str:
    if not api_key:
        api_key:str = os.environ.get("ELEVEN_LABS_API_KEY",None)
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

class VoiceGeneratorElevenLabs:
    """
    Voice Generates through Eleven Labs
    """
    
    def __init__(self,api_key:str|None = None)->None:
        api_key = validate_api_key(api_key)
        self.client = AsyncElevenLabs(api_key = api_key)
        
    async def generate(
        self,
        text:str,
        voice_id : str,
        model:str = "eleven_multilingual_v2",
        stability: builtins.float = 0.5,
        similarity_boost:bool = True,
        style: builtins.float = 0.0,
        use_speaker_boost:bool = True 
    ):
        """
        Generate voice audio from text given as input
        
        Args:
            text : text input to convert to speech
            voice_id : ElevenLabs voice ID
            model : Model NAME
            stability : Voice Stability
            similarity_boost : -
            style : Style exaggeration
            use_speaker_boost : enable Speaker boost
            
        output:
            generated results from audio data
    
        """
        
        voice_settings = VoiceSettings(
            stability=stability,
            similarity_boost=similarity_boost,
            style = style,
            use_speaker_boost=use_speaker_boost
        )
        
        generator_audio = await self.client.text_to_speech(
            text = text,
            voice_id = voice_id,
            model_id = model,
            voice_settings = VoiceSettings
        )
        
        audio_chunks : list[bytes] = []
        async for chunk in generator_audio:
            audio_chunks.append(chunk)
        
        data = b"".join(audio_chunks)
        
        cost = self.estimated_cost(text,model)   
        
        return GeneratedVoiceResult(
            voices = [
                GeneratedVoice(
                    audio_data=data,
                    generated_at=datetime.datetime.now().isoformat()
                )
            ],
            text = text,
            voice_id=voice_id,
            model=model,
            cost = cost
        )
        

        
        
             
        
    
    
