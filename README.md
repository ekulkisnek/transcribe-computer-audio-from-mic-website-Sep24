
# Live Audio Transcription App

A Flask-based web application that provides real-time audio transcription using DeepSpeech. The app allows users to record audio through their browser and receive instant text transcriptions.

## Features

- Real-time audio recording and transcription
- WebSocket-based communication for instant results
- Transcript history storage
- Error logging and viewing
- Responsive web interface

## Technical Stack

- Backend: Flask + Flask-SocketIO
- Database: SQLAlchemy
- Speech Recognition: Mozilla DeepSpeech
- Frontend: HTML, CSS, JavaScript with WebSocket support

## Setup

The application requires DeepSpeech models to function. These will be downloaded automatically when the project starts.

Required models:
- deepspeech-0.9.3-models.pbmm
- deepspeech-0.9.3-models.scorer

## Usage

1. Click the "Start Recording" button to begin audio capture
2. Speak into your microphone
3. Click "Stop Recording" when finished
4. View transcription results in real-time
5. Check transcript history below
6. Use "View Errors" button to check for any issues

## Architecture

- `main.py`: Main Flask application and WebSocket handlers
- `transcription.py`: DeepSpeech integration and audio processing
- `database.py`: SQLAlchemy models and database initialization
- `config.py`: Application configuration
- Frontend files in `static/` and `templates/` directories
