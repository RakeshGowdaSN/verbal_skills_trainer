import sys
import os
import pytest
from fastapi.testclient import TestClient
from fastapi import UploadFile
from io import BytesIO

# Get the absolute path to the 'backend' directory
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Add the 'backend' directory to sys.path
sys.path.append(backend_dir)

from main import app  # Now the import should work

client = TestClient(app)

# Helper function to create a dummy audio file
def create_dummy_audio_file(filename="test.wav", content=b"dummy audio data"):
    """Creates a dummy audio file for testing."""
    file_path = os.path.join(backend_dir, filename)
    with open(file_path, "wb") as f:
        f.write(content)
    return file_path

def test_chat():
    response = client.post("/chat/", json={"message": "Hello, how are you?", "role": "speech_coach", "model": "openai"})
    assert response.status_code == 200
    assert "response" in response.json()

def test_chat_xai():
    response = client.post("/chat/", json={"message": "Hello, how are you?", "role": "speech_coach", "model": "xai"})
    assert response.status_code == 200
    assert "response" in response.json()

def test_chat_invalid_model():
    response = client.post("/chat/", json={"message": "Hello", "role": "speech_coach", "model": "invalid"})
    assert response.status_code == 400
    assert "detail" in response.json()
    assert response.json()["detail"] == "Invalid model selected."

def test_voice_input():
    # Create a dummy audio file
    audio_file_path = create_dummy_audio_file()

    with open(audio_file_path, "rb") as audio_file:
        files = {"audio": ("test.wav", audio_file, "audio/wav")}
        response = client.post("/voice/", files=files)

    # Clean up the dummy audio file
    os.remove(audio_file_path)

    assert response.status_code == 200
    assert "transcript" in response.json()
    assert "response" in response.json()
    assert "audio_feedback" in response.json()

def test_assess_presentation_text():
    response = client.post("/assess/", params={"text": "This is a test presentation."})
    assert response.status_code == 200
    assert "feedback" in response.json()

def test_assess_presentation_audio():
    # Create a dummy audio file
    audio_file_path = create_dummy_audio_file()

    with open(audio_file_path, "rb") as audio_file:
        files = {"audio": ("test.wav", audio_file, "audio/wav")}
        response = client.post("/assess/", files=files)

    # Clean up the dummy audio file
    os.remove(audio_file_path)

    assert response.status_code == 200
    assert "feedback" in response.json()

def test_train_impromptu():
    response = client.post("/train/", json={"user_input": "Explain teamwork.", "module": "impromptu", "model": "openai"})
    assert response.status_code == 200
    assert "feedback" in response.json()
    assert "message" in response.json()
    assert response.json()["message"] == "Feedback for impromptu training."

def test_train_storytelling():
    response = client.post("/train/", json={"user_input": "Once upon a time...", "module": "storytelling", "model": "openai"})
    assert response.status_code == 200
    assert "feedback" in response.json()
    assert "message" in response.json()
    assert response.json()["message"] == "Feedback for storytelling training."

def test_train_conflict_resolution():
    response = client.post("/train/", json={"user_input": "You missed the deadline!", "module": "conflict_resolution", "model": "openai"})
    assert response.status_code == 200
    assert "feedback" in response.json()
    assert "message" in response.json()
    assert response.json()["message"] == "Feedback for conflict_resolution training."

def test_train_invalid_module():
    response = client.post("/train/", json={"user_input": "Test", "module": "invalid", "model": "openai"})
    assert response.status_code == 400
    assert "detail" in response.json()
    assert response.json()["detail"] == "Invalid training module."

def test_train_invalid_model():
    response = client.post("/train/", json={"user_input": "Test", "module": "impromptu", "model": "invalid"})
    assert response.status_code == 400
    assert "detail" in response.json()
    assert response.json()["detail"] == "Invalid model selected."

def test_audio_endpoint():
    # Create the audio_files directory if it doesn't exist
    audio_files_dir = os.path.join(backend_dir, "audio_files")
    os.makedirs(audio_files_dir, exist_ok=True)

    # Create a dummy audio file
    audio_file_path = os.path.join(audio_files_dir, "test_audio.mp3")
    with open(audio_file_path, "wb") as f:
        f.write(b"dummy audio data")

    response = client.get("/audio/test_audio.mp3")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/octet-stream"  # Updated content type

    # Clean up the dummy audio file
    os.remove(audio_file_path)

def test_audio_endpoint_invalid_filename():
    response = client.get("/audio/../test.mp3")
    assert response.status_code == 400
    assert "detail" in response.json()
    assert response.json()["detail"] == "Invalid filename"

def test_audio_endpoint_not_found():
    response = client.get("/audio/nonexistent.mp3")
    assert response.status_code == 404
    assert "detail" in response.json()
    assert response.json()["detail"] == "Audio file not found"