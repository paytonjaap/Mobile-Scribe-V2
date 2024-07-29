const recordButton = document.getElementById('recordButton');
const sendButton = document.getElementById('sendButton');
const transcriptDiv = document.getElementById('transcript');
const summaryDiv = document.getElementById('summary');
const emailInput = document.getElementById('email');
const audioContainer = document.getElementById('audioContainer');
let isRecording = false;
let finalTranscript = '';
let mediaRecorder;
let audioChunks = [];

function uploadAudio(blob) {
    const formData = new FormData();
    formData.append('audio', blob);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        finalTranscript = data.transcription;
        transcriptDiv.textContent = finalTranscript;
        summaryDiv.textContent = data.summary;
    })
    .catch(error => {
        console.error('Error uploading audio:', error);
    });
}

recordButton.addEventListener('click', async () => {
    if (isRecording) {
        mediaRecorder.stop();
        recordButton.textContent = 'Start Recording';
    } else {
        finalTranscript = '';
        transcriptDiv.textContent = '';
        summaryDiv.textContent = '';
        audioChunks = [];

        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);

            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const audioUrl = URL.createObjectURL(audioBlob);
                const audio = document.createElement('audio');
                const downloadLink = document.createElement('a');

                audio.src = audioUrl;
                audio.controls = true;
                downloadLink.href = audioUrl;
                downloadLink.download = 'recording.wav';
                downloadLink.textContent = 'Download Recording';

                audioContainer.innerHTML = '';
                audioContainer.appendChild(audio);
                audioContainer.appendChild(downloadLink);

                // Upload the audio for processing
                uploadAudio(audioBlob);
            };

            mediaRecorder.start();
            recordButton.textContent = 'Stop Recording';
        } else {
            alert('Your browser does not support audio recording.');
        }
    }
    isRecording = !isRecording;
});

sendButton.addEventListener('click', () => {
    const email = emailInput.value;
    if (email && finalTranscript) {
        const mailtoLink = `mailto:${email}?subject=Transcription&body=${encodeURIComponent(finalTranscript)}`;
        window.location.href = mailtoLink;
    } else {
        alert('Please enter a valid email and ensure there is a transcription to send.');
    }
});
