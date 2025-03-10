from gtts import gTTS
import os
import json
import openai
from openai import RateLimitError, OpenAIError
from utils.constants import OPENAI_API_KEY, OPENAI_ORGANIZATION, OPENAI_PROJECT, XAI_API_KEY, MODEL_NAME
from utils.database import save_presentation_feedback
import time
from fastapi import HTTPException
from config import logger


# client = openai.OpenAI(
#     api_key=OPENAI_API_KEY,
#     organization=OPENAI_ORGANIZATION,
#     project=OPENAI_PROJECT
# )

client = openai.OpenAI(
    api_key=OPENAI_API_KEY
)

# client = openai.OpenAI(
#     api_key=XAI_API_KEY,
#     base_url="https://api.x.ai/v1"
# )


def evaluate_presentation(presentation_text: str, method: str = "text") -> dict:
    """Evaluate user's presentation and return structured feedback."""
    prompt = f"Analyze this {method} presentation:\n{presentation_text}\nProvide feedback on structure, delivery, and content. Return a JSON object with scores out of 10 for each category, and a full report. Example: {{'structure_score': 8, 'delivery_score': 9, 'content_score': 7, 'full_report': '...'}}"
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        feedback_json = response.choices[0].message.content
        try:
          feedback = json.loads(feedback_json)
        except json.JSONDecodeError:
          feedback = {"full_report": feedback_json}
        save_presentation_feedback(presentation_text, feedback.get("full_report", feedback_json))
        return feedback
    except Exception as e:
        logger.error(f"Error evaluating presentation: {e}")
        raise HTTPException(status_code=500, detail="Error evaluating presentation.")

def text_to_speech(text: str, output_file: str = None):
    """Convert AI feedback to speech for audio feedback."""
    if output_file is None:
        output_file = f"audio_files/output_{time.time()}.mp3"
    os.makedirs("audio_files", exist_ok=True)
    tts = gTTS(text=text, lang='en')
    tts.save(output_file)
    return output_file.split("/")[-1]

def safe_api_call(func, *args, max_retries=5, initial_delay=1, **kwargs):
    """Retries OpenAI API calls with exponential backoff."""
    retries = 0
    delay = initial_delay

    while retries < max_retries:
        try:
            return func(*args, **kwargs)
        except RateLimitError as e:
            retries += 1
            if retries == max_retries:
                logger.error(f"Max retries reached. OpenAI RateLimitError: {e}")
                raise  # Re-raise the exception
            logger.warning(f"RateLimitError: Retrying in {delay} seconds (attempt {retries}/{max_retries}).")
            time.sleep(delay)
            delay *= 2  # Exponential backoff
        except OpenAIError as e:
            logger.error(f"OpenAIError: {e}")
            raise e #re raise other openAI errors.
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise e
    return None