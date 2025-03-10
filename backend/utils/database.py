import json
import os
from config import logger  # Import the logger

DB_FILE = "progress.json"

def save_user_progress(user_input: str, ai_feedback: str, module: str):
    """Save user responses and feedback for training modules."""
    try:
        data = load_progress()
        data.append({"module": module, "input": user_input, "feedback": ai_feedback})

        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        logger.info(f"Saved user progress for module: {module}")
    except Exception as e:
        logger.error(f"Error saving user progress: {e}")

def save_presentation_feedback(presentation: str, feedback: str):
    """Save presentation assessments."""
    try:
        data = load_progress()
        data.append({"type": "presentation", "input": presentation, "feedback": feedback})

        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        logger.info("Saved presentation feedback")
    except Exception as e:
        logger.error(f"Error saving presentation feedback: {e}")

def load_progress():
    """Load progress tracking file."""
    try:
        if not os.path.exists(DB_FILE):
            return []

        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Database file not found: {DB_FILE}")
        return []
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from {DB_FILE}.  Returning empty list.  Consider manual inspection/correction of the file.")
        return []
    except Exception as e:
        logger.error(f"Error loading progress: {e}")
        return []