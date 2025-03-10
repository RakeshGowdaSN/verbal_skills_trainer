import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ORGANIZATION = os.getenv("OPENAI_ORGANIZATION")
OPENAI_PROJECT = os.getenv("OPENAI_PROJECT")

XAI_API_KEY = os.getenv("XAI_API_KEY")

# # Supported AI Roles
# SUPPORTED_ROLES = {
#     "job_interviewer": "You are a professional job interviewer. Ask structured questions, assess responses, and give feedback on clarity and conciseness.",
#     "debate_partner": "You are a debate opponent. Challenge arguments logically, ask counter-questions, and give constructive feedback.",
#     "speech_coach": "Analyze verbal delivery. Provide feedback on pacing, filler words, and clarity.",
#     "casual_conversation": "You are a friendly conversation partner. Engage in a natural chat and help improve fluency."
# }

TRAINING_MODULES = {
    "impromptu": "impromptu",
    "storytelling": "storytelling",
    "conflict_resolution": "conflict_resolution"
}

OPENAI_MODELS = ["gpt-4o-mini","gpt-3.5-turbo", "gpt-4"]
XAI_MODELS = ["grok-2-latest"]

MODEL_NAME = "gpt-4o-mini" #Default model.
TEMPERATURE = 0.2
MAX_TOKENS = 1024
TOP_P = 0.95
FREQUENCY_PENALTY = 0.1
PRESENCE_PENALTY = 0.1

# Default AI Role
DEFAULT_ROLE = "coach"