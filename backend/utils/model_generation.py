import openai
from utils.constants import MODEL_NAME, OPENAI_API_KEY
from prompts.prompt_templates import PROMPTS
from utils.database import save_user_progress
from config import logger
import io

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

def get_ai_response(user_input: str, role: str, api_key: str, model_name: str) -> str:
    """
    Generate AI response based on the user's message and selected role.
    The prompt is built using templates from prompt_templates.py.
    """

    logger.info("Generating AI response")

    # # Testing
    # logger.debug(f"Key: {OPENAI_API_KEY}")
    # logger.debug(f"client: {client}")

    # Use the corresponding prompt template or default to 'speech_coach'
    prompt_template = PROMPTS.get(role, PROMPTS.get("speech_coach"))
    prompt = f"{prompt_template}\nUser: {user_input}\nAI:"
    logger.debug(f"Using prompt: {prompt}")

    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}]
        )

        ai_response = response.choices[0].message.content
        logger.debug(f"Received ai_response: {ai_response}")
        # Save progress in our local storage (JSON/SQLite)
        save_user_progress(role, user_input, ai_response)
        return ai_response
    except openai.OpenAIError as e:
        logger.error(f"OpenAI error: {e}")
        return "An error occurred with the OpenAI service. Please try again later."
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return "An unexpected error occurred. Please try again later."

def transcribe_audio(audio_data: bytes) -> str:
    """Transcribe audio using Whisper API."""

    try:
        # Create a BytesIO object from the audio bytes
        audio_file = io.BytesIO(audio_data)
        audio_file.name = "audio.mp3"  # Set a filename (important for Whisper)
        audio_file.seek(0)  # Reset the file pointer to the beginning

        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
        logger.debug(f"transcribe audio response: {response}")
        return response
    except openai.OpenAIError as e:
        logger.error(f"OpenAI error: {e}")
        return "Could not transcribe audio. Please try again later."
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return "Could not transcribe audio. Please try again later."