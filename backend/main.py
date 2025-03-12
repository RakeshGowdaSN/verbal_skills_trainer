from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import RateLimitError, AuthenticationError, BadRequestError, OpenAIError
import os
from fastapi.responses import FileResponse
import time
import re

# User Defined functions
from utils.model_generation import get_ai_response, transcribe_audio
from utils.helper_functions import evaluate_presentation, safe_api_call, text_to_speech
from config import logger
from utils.constants import TRAINING_MODULES, MODEL_NAME, XAI_MODELS

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
XAI_API_KEY = os.getenv("XAI_API_KEY")

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost",  # Allow requests from localhost
    "http://localhost:3000", # Allow requests from port 3000
    "http://localhost:8080", # Allow requests from port 8080
    # Add other origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

class ChatRequest(BaseModel):
    message: str
    role: str
    model: str = "openai"

class TrainingRequest(BaseModel):
    user_input: str
    module: str
    model: str = "openai"

@app.get("/")
async def onboarding():
    return {"message": "Welcome to the Verbal Skills Trainer! Use /chat, /voice, /assess, and /train endpoints."}

@app.post("/chat/")
async def chat(request: ChatRequest):
    logger.info(f"Received chat request for model: {request.model}")
    logger.debug(f"ChatRequest payload: {request.model_dump()}")
    
    try:
        if request.model == "openai":
            ai_response = safe_api_call(get_ai_response, request.message, request.role, OPENAI_API_KEY, MODEL_NAME)
        elif request.model == "xai":
            ai_response = safe_api_call(get_ai_response, request.message, request.role, XAI_API_KEY, XAI_MODELS[0])
        else:
            raise HTTPException(status_code=400, detail="Invalid model selected.")
        
        logger.debug(f"AI Response: {ai_response}")
        return {"response": ai_response}

    except RateLimitError as e:
        logger.error(f"Rate limit error: {e}")
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    except AuthenticationError as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Authentication error. Please check your API key.")
    except BadRequestError as e:
        logger.error(f"Bad request error: {e}")
        raise HTTPException(status_code=400, detail="Bad request. Please check your input.")
    except OpenAIError as e:
        logger.error(f"OpenAI error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred with the OpenAI service. Please try again later.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again later.")

@app.post("/voice/")
async def voice_input(audio: UploadFile = File(...)):
    logger.info("Received voice input")
    try:
        audio_bytes = await audio.read()
        transcript = safe_api_call(transcribe_audio, audio_bytes)
        logger.debug(f"Transcribed text: {transcript}")

        # Check if transcription was successful
        if transcript == "Could not transcribe audio. Please try again later.":
            logger.error("Transcription failed.")
            return {"transcript": transcript, "response": "Transcription failed. Please try again."}

        # Modified prompt to include vocal delivery analysis
        prompt = f"Analyze this speech transcription:\n{transcript}\nProvide feedback on vocal delivery, including pacing, filler words, and clarity. Also provide general feedback on the content."
        ai_response = safe_api_call(get_ai_response, prompt, "speech_coach", OPENAI_API_KEY, MODEL_NAME) 
        logger.debug(f"Voice AI Response: {ai_response}")
        speech_file = text_to_speech(ai_response)
        return {"transcript": transcript, "response": ai_response, "audio_feedback": speech_file}
        # return {"transcript": transcript, "response": ai_response}

    except RateLimitError as e:
        logger.error(f"Rate limit error: {e}")
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    except AuthenticationError as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Authentication error. Please check your API key.")
    except BadRequestError as e:
        logger.error(f"Bad request error: {e}")
        raise HTTPException(status_code=400, detail="Bad request. Please check your input.")
    except OpenAIError as e:
        logger.error(f"OpenAI error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred with the OpenAI service. Please try again later.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again later.")

@app.post("/train/")
async def train(request: TrainingRequest):
    logger.info(f"Received training request: {request.module}")
    if request.module not in TRAINING_MODULES:
        raise HTTPException(status_code=400, detail="Invalid training module.")
    
    try:
        if request.model == "openai":
            feedback = safe_api_call(get_ai_response, request.user_input, request.module, OPENAI_API_KEY, MODEL_NAME)
        elif request.model == "xai":
            feedback = safe_api_call(get_ai_response, request.user_input, request.module, XAI_API_KEY, XAI_MODELS[0])
        else:
            raise HTTPException(status_code=400, detail="Invalid model selected.")
            
        logger.debug(f"Training feedback: {feedback}")
        return {"feedback": feedback, "message": f"Feedback for {request.module} training."}
    except RateLimitError as e:
        logger.error(f"Rate limit error: {e}")
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    except AuthenticationError as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Authentication error. Please check your API key.")
    except BadRequestError as e:
        logger.error(f"Bad request error: {e}")
        raise HTTPException(status_code=400, detail="Bad request. Please check your input.")
    except OpenAIError as e:
        logger.error(f"OpenAI error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred with the OpenAI service. Please try again later.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again later.")
    
@app.post("/assess/text/")
async def assess_presentation_text(text: str = Form(...)):
    logger.info("Received text presentation assessment request")
    try:
        presentation_text = text
        method = "text"
        logger.debug("Processing text presentation")

        feedback = safe_api_call(evaluate_presentation, presentation_text, method)
        logger.info("Presentation evaluation completed")
        logger.debug(f"Evaluation feedback: {feedback}")
        return {"feedback": feedback}
    except RateLimitError as e:
        logger.error(f"Rate limit error: {e}")
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    except AuthenticationError as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Authentication error. Please check your API key.")
    except BadRequestError as e:
        logger.error(f"Bad request error: {e}")
        raise HTTPException(status_code=400, detail="Bad request. Please check your input.")
    except OpenAIError as e:
        logger.error(f"OpenAI error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred with the OpenAI service. Please try again later.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again later.")

@app.post("/assess/voice/")
async def assess_presentation_voice(audio: UploadFile = File(...)):
    logger.info("Received voice presentation assessment request")
    try:
        audio_bytes = await audio.read()
        presentation_text = safe_api_call(transcribe_audio, audio_bytes)
        method = "voice"
        logger.debug("Processing voice presentation")

        # Check if transcription was successful
        if presentation_text == "Could not transcribe audio. Please try again later.":
            logger.error("Transcription failed.")
            return {"feedback": "Transcription failed. Please try again."}

        feedback = safe_api_call(evaluate_presentation, presentation_text, method)
        logger.info("Presentation evaluation completed")
        logger.debug(f"Evaluation feedback: {feedback}")
        return {"feedback": feedback}
    except RateLimitError as e:
        logger.error(f"Rate limit error: {e}")
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    except AuthenticationError as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Authentication error. Please check your API key.")
    except BadRequestError as e:
        logger.error(f"Bad request error: {e}")
        raise HTTPException(status_code=400, detail="Bad request. Please check your input.")
    except OpenAIError as e:
        logger.error(f"OpenAI error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred with the OpenAI service. Please try again later.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again later.")

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """Serve audio files."""
    # Sanitize the filename to prevent path traversal attacks
    if not re.match(r"^[a-zA-Z0-9._-]+$", filename):
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = f"audio_files/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="Audio file not found")