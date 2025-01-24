import deepspeech
import numpy as np
import logging
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load DeepSpeech model
MODEL_FILE_PATH = "deepspeech-0.9.3-models.pbmm"
SCORER_FILE_PATH = "deepspeech-0.9.3-models.scorer"

model = None

def load_model():
    global model
    model = deepspeech.Model(MODEL_FILE_PATH)
    model.enableExternalScorer(SCORER_FILE_PATH)

def transcribe_audio(audio_data):
    try:
        if model is None:
            load_model()

        logger.info(f"Starting transcription process for audio of size: {len(audio_data)} bytes")
        
        # Convert audio data to 16-bit int array
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        # Perform speech-to-text
        text = model.stt(audio_array)
        
        logger.info(f"Transcription completed. Length: {len(text)} characters")
        logger.info(f"Transcription result: {text[:100]}...")  # Log the first 100 characters of the transcript
        return text
    except Exception as e:
        logger.exception(f"Error in transcribe_audio: {str(e)}")
        return None
