from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from config import Config
from database import db, Transcript, init_db
from transcription import transcribe_audio, load_model
import base64
import io
import logging
from logging.handlers import RotatingFileHandler
import os
import numpy as np

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app)
init_db(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up file handler for error logging
error_log_path = os.path.join(app.root_path, 'error_log.txt')
file_handler = RotatingFileHandler(error_log_path, maxBytes=10000, backupCount=1)
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
app.logger.addHandler(file_handler)

def preprocess_audio(audio_data):
    try:
        # Convert base64 audio data to numpy array
        audio_np = np.frombuffer(base64.b64decode(audio_data), dtype=np.int16)
        return audio_np.tobytes()
    except Exception as e:
        app.logger.error(f"Error in preprocess_audio: {str(e)}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcripts', methods=['GET'])
def get_transcripts():
    transcripts = Transcript.query.order_by(Transcript.created_at.desc()).all()
    return jsonify([{'id': t.id, 'content': t.content, 'created_at': t.created_at} for t in transcripts])

@app.route('/errors', methods=['GET'])
def get_errors():
    try:
        with open(error_log_path, 'r') as error_file:
            errors = error_file.read()
        return jsonify({'errors': errors})
    except Exception as e:
        return jsonify({'error': f'Failed to read error log: {str(e)}'}), 500

@socketio.on('transcribe')
def handle_transcribe(data):
    try:
        audio_data = data['audio']
        app.logger.info(f"Received audio data size: {len(audio_data)} bytes")
        
        preprocessed_audio = preprocess_audio(audio_data)
        if preprocessed_audio is None:
            raise ValueError("Audio preprocessing failed")
        
        app.logger.info(f"Preprocessed audio size: {len(preprocessed_audio)} bytes")
        
        transcript = transcribe_audio(preprocessed_audio)
        
        if transcript:
            app.logger.info(f"Transcription successful. Length: {len(transcript)} characters")
            socketio.emit('transcription_result', {'content': transcript})
            new_transcript = Transcript(content=transcript)
            db.session.add(new_transcript)
            db.session.commit()
        else:
            error_msg = "Transcription failed: No transcript returned"
            app.logger.error(error_msg)
            socketio.emit('transcription_error', {'message': error_msg})
    except Exception as e:
        error_msg = f"Error in handle_transcribe: {str(e)}"
        app.logger.exception(error_msg)
        socketio.emit('transcription_error', {'message': error_msg})

if __name__ == '__main__':
    load_model()  # Load the DeepSpeech model before starting the server
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
