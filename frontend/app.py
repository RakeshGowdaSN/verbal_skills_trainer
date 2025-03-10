import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")  # Default to localhost if not set

st.title("Verbal Skills Trainer")

# Model Selection
model_choice = st.selectbox("Select Model:", ["OpenAI", "XAI (Grok)"])
selected_model = "openai" if model_choice == "OpenAI" else "xai"

# Chat Interface
st.header("Chat")
chat_message = st.text_input("Enter your chat message:")
chat_role = st.selectbox("Select role:", ["speech_coach"])
if st.button("Send Chat"):
    if chat_message:
        try:
            response = requests.post(f"{API_URL}/chat/", json={"message": chat_message, "role": chat_role, "model": selected_model})
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            result = response.json()
            st.write(f"Response: {result['response']}")
        except requests.exceptions.RequestException as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please enter a message.")

# Voice Input
st.header("Voice Input")
uploaded_audio = st.file_uploader("Upload audio file", type=["wav", "mp3", "mp4"])
if st.button("Process Voice"):
    if uploaded_audio:
        try:
            files = {"audio": (uploaded_audio.name, uploaded_audio, uploaded_audio.type)}
            response = requests.post(f"{API_URL}/voice/", files=files)
            response.raise_for_status()
            result = response.json()
            st.write(f"Transcript: {result['transcript']}")
            st.write(f"Response: {result['response']}")
            st.audio(result['audio_feedback'], format="audio/mpeg")  # Assuming audio_feedback is an audio file path
        except requests.exceptions.RequestException as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please upload an audio file.")

# Assess Presentation (Text)
st.header("Assess Presentation (Text)")
presentation_text = st.text_area("Enter your presentation text:")
if st.button("Assess Text"):
    if presentation_text:
        try:
            response = requests.post(f"{API_URL}/assess/", params={"text": presentation_text})
            response.raise_for_status()
            result = response.json()
            st.write(f"Feedback: {result['feedback']}")
            st.audio(result['audio_feedback'], format="audio/mpeg")
        except requests.exceptions.RequestException as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please enter presentation text.")

# Assess Presentation (Audio)
st.header("Assess Presentation (Audio)")
uploaded_presentation_audio = st.file_uploader("Upload presentation audio", type=["wav", "mp3", "mp4"])
if st.button("Assess Audio"):
    if uploaded_presentation_audio:
        try:
            files = {"audio": (uploaded_presentation_audio.name, uploaded_presentation_audio, uploaded_presentation_audio.type)}
            response = requests.post(f"{API_URL}/assess/", files=files)
            response.raise_for_status()
            result = response.json()
            st.write(f"Feedback: {result['feedback']}")
            st.audio(result['audio_feedback'], format="audio/mpeg")
        except requests.exceptions.RequestException as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please upload presentation audio.")

# Training Modules
st.header("Training Modules")
training_module = st.selectbox("Select training module:", ["impromptu", "storytelling", "conflict_resolution"])
training_input = st.text_area("Enter your training input:")
if st.button("Start Training"):
    if training_input:
        try:
            response = requests.post(f"{API_URL}/train/", json={"user_input": training_input, "module": training_module})
            response.raise_for_status()
            result = response.json()
            st.write(f"Feedback: {result['feedback']}")
            st.write(f"Message: {result['message']}")
        except requests.exceptions.RequestException as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please enter training input.")

# Audio File Display (Optional)
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