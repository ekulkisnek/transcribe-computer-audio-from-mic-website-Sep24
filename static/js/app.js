let mediaRecorder;
let audioChunks = [];
let isRecording = false;

const startButton = document.getElementById('startButton');
const stopButton = document.getElementById('stopButton');
const viewErrorsButton = document.getElementById('viewErrorsButton');
const transcriptDiv = document.getElementById('transcript');
const historyDiv = document.getElementById('history');
const errorDiv = document.getElementById('errorDiv');

const socket = io();

startButton.addEventListener('click', startRecording);
stopButton.addEventListener('click', stopRecording);
viewErrorsButton.addEventListener('click', viewErrors);

function indicateNewError() {
    viewErrorsButton.classList.add('new-error');
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
            if (audioChunks.length > 0) {
                sendAudioChunksToServer();
            }
        };

        mediaRecorder.start(1000); // Collect data every second
        isRecording = true;
        startButton.disabled = true;
        stopButton.disabled = false;
    } catch (err) {
        console.error('Error accessing microphone:', err);
        alert('Error accessing microphone. Please check your settings and try again.');
    }
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        startButton.disabled = false;
        stopButton.disabled = true;
    }
}

function sendAudioChunksToServer() {
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
    audioChunks = [];

    const reader = new FileReader();
    reader.onloadend = () => {
        const base64Audio = reader.result.split(',')[1];
        socket.emit('transcribe', { audio: base64Audio });
    };
    reader.readAsDataURL(audioBlob);
}

socket.on('transcription_result', (data) => {
    const transcriptElement = document.createElement('span');
    transcriptElement.textContent = data.content + ' ';
    transcriptDiv.appendChild(transcriptElement);
    transcriptDiv.scrollTop = transcriptDiv.scrollHeight;
});

socket.on('transcription_error', (data) => {
    console.error('Transcription error:', data.message);
    indicateNewError();
});

function loadTranscriptHistory() {
    fetch('/transcripts')
        .then(response => response.json())
        .then(transcripts => {
            historyDiv.innerHTML = '<h2>Transcript History</h2>';
            transcripts.forEach(transcript => {
                const transcriptElement = document.createElement('div');
                transcriptElement.className = 'transcript-item';
                transcriptElement.innerHTML = `
                    <p>${transcript.content}</p>
                    <small>${new Date(transcript.created_at).toLocaleString()}</small>
                `;
                historyDiv.appendChild(transcriptElement);
            });
        })
        .catch(error => console.error('Error loading transcript history:', error));
}

function viewErrors() {
    fetch('/errors')
        .then(response => response.json())
        .then(data => {
            errorDiv.innerHTML = '<h2>Error Log</h2>';
            if (data.errors) {
                const errorPre = document.createElement('pre');
                errorPre.textContent = data.errors;
                errorDiv.appendChild(errorPre);
            } else {
                errorDiv.innerHTML += '<p>No errors found.</p>';
            }
            errorDiv.style.display = 'block';
            viewErrorsButton.classList.remove('new-error');

            const hideErrorsButton = document.createElement('button');
            hideErrorsButton.textContent = 'Hide Errors';
            hideErrorsButton.addEventListener('click', () => {
                errorDiv.style.display = 'none';
            });
            errorDiv.appendChild(hideErrorsButton);
        })
        .catch(error => {
            console.error('Error fetching error log:', error);
            errorDiv.innerHTML = '<h2>Error Log</h2><p>Failed to fetch error log.</p>';
            errorDiv.style.display = 'block';
        });
}

document.addEventListener('DOMContentLoaded', loadTranscriptHistory);
