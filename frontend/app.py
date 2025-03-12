import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")  # Default to localhost if not set

st.title("Verbal Skills Trainer")

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

def make_api_request(endpoint, method="POST", data=None, files=None):
    """Helper function to make API requests with error handling."""
    try:
        url = f"{API_URL}{endpoint}"
        if method == "POST":
            if files:
                response = requests.post(url, files=files)
            else:
                response = requests.post(url, json=data)
        else:
            response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")
        return None

# -----------------------------------------------------------------------------
# Model Selection
# -----------------------------------------------------------------------------

model_choice = st.selectbox("Select Model:", ["OpenAI", "XAI (Grok)"])
selected_model = "openai" if model_choice == "OpenAI" else "xai"

# -----------------------------------------------------------------------------
# Chat Interface
# -----------------------------------------------------------------------------

st.header("Chat")
chat_message = st.text_input("Enter your chat message:")
chat_role = st.selectbox("Select role:", ["speech_coach", "job_interviewer", "debate_partner"])

if st.button("Send Chat"):
    if chat_message:
        data = {"message": chat_message, "role": chat_role, "model": selected_model}
        result = make_api_request("/chat/", data=data)
        if result:
            st.write(f"Response: {result['response']}")
    else:
        st.warning("Please enter a message.")

# -----------------------------------------------------------------------------
# Voice Input
# -----------------------------------------------------------------------------

st.header("Voice Input")
uploaded_audio = st.file_uploader("Upload audio file", type=["wav", "mp3", "mp4"])

if st.button("Process Voice"):
    if uploaded_audio:
        files = {"audio": (uploaded_audio.name, uploaded_audio, uploaded_audio.type)}
        result = make_api_request("/voice/", files=files)
        if result:
            st.write(f"Transcript: {result['transcript']}")
            st.write(f"Response: {result['response']}")
            if 'audio_feedback' in result:
                st.audio(result['audio_feedback'], format="audio/mpeg")  # Assuming audio_feedback is an audio file path
    else:
        st.warning("Please upload an audio file.")

# -----------------------------------------------------------------------------
# Training Modules
# -----------------------------------------------------------------------------

st.header("Training Modules")
training_module = st.selectbox("Select training module:", ["impromptu", "storytelling", "conflict_resolution"])
training_input = st.text_area("Enter your training input:")

if st.button("Start Training"):
    if training_input:
        data = {"user_input": training_input, "module": training_module, "model": selected_model}
        result = make_api_request("/train/", data=data)
        if result:
            st.write(f"Feedback: {result['feedback']}")
            st.write(f"Message: {result['message']}")
    else:
        st.warning("Please enter training input.")
        
# -----------------------------------------------------------------------------
# Assess Presentation (Text)
# -----------------------------------------------------------------------------

st.header("Assess Presentation (Text)")
presentation_text = st.text_area("Enter your presentation text:")

if st.button("Assess Text"):
    if presentation_text:
        data = {"text": presentation_text}
        result = make_api_request("/assess/text/", data=data)
        if result:
            st.write(f"Feedback: {result['feedback']}")
    else:
        st.warning("Please enter presentation text.")

# -----------------------------------------------------------------------------
# Assess Presentation (Audio)
# -----------------------------------------------------------------------------

st.header("Assess Presentation (Audio)")
uploaded_presentation_audio = st.file_uploader("Upload presentation audio", type=["wav", "mp3", "mp4"])

if st.button("Assess Audio"):
    if uploaded_presentation_audio:
        files = {"audio": (uploaded_presentation_audio.name, uploaded_presentation_audio, uploaded_presentation_audio.type)}
        result = make_api_request("/assess/voice/", files=files)
        if result:
            st.write(f"Feedback: {result['feedback']}")
    else:
        st.warning("Please upload presentation audio.")

# -----------------------------------------------------------------------------
# Audio File Display (Optional)
# -----------------------------------------------------------------------------

st.header("Audio File Display")
audio_file_name = st.text_input("Enter audio file name (e.g., test_audio.mp3):")

if st.button("Display Audio"):
    if audio_file_name:
        try:
            response = requests.get(f"{API_URL}/audio/{audio_file_name}")
            response.raise_for_status()
            st.audio(response.content, format="audio/mpeg")
        except requests.exceptions.RequestException as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please enter an audio file name.")