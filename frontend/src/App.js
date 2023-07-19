import React, { useState, useRef } from 'react';
import axios from 'axios';

function App() {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [transcription, setTranscription] = useState('');
  const [imageUrl, setImageUrl] = useState('');
  const mediaRecorderRef = useRef(null);
  const audioPlayerRef = useRef(null);

  const startRecording = () => {
    const mediaConstraints = { audio: true };
    navigator.mediaDevices.getUserMedia(mediaConstraints)
      .then((stream) => {
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        const chunks = [];
        mediaRecorder.ondataavailable = (event) => {
          chunks.push(event.data);
        };
        mediaRecorder.onstop = () => {
          const audioBlob = new Blob(chunks, { type: 'audio/webm' });
          setAudioBlob(audioBlob);
        };
        mediaRecorder.start();
        setIsRecording(true);
      })
      .catch((error) => {
        console.error('Error accessing media devices:', error);
      });
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const playRecording = () => {
    if (audioPlayerRef.current && audioBlob) {
      const audioUrl = URL.createObjectURL(audioBlob);
      audioPlayerRef.current.src = audioUrl;
      audioPlayerRef.current.play();
    }
  };

  const submitAudio = () => {
    if (audioBlob) {
      const formData = new FormData();
      formData.append('audio_file', audioBlob, 'recording.webm');
      // console.log(formData.get('audio_file'));

      axios.post('http://localhost:8000/api/process-audio/', formData)
        .then(response => {
          console.log('Response from server:', response.data);
          const { transcription, image_url } = response.data;
          setTranscription(transcription);
          setImageUrl(image_url);
        })
        .catch(error => {
          console.error('Error sending audio to the server:', error);
        });
    }
  };

  return (
    <div>
      <h1>Speech-to-Text-to-Image Application</h1>
      <div>
        <button onClick={startRecording} disabled={isRecording}>
          Start Recording
        </button>
        <button onClick={stopRecording} disabled={!isRecording}>
          Stop Recording
        </button>
        <button onClick={playRecording} disabled={!audioBlob}>
          Play Recording
        </button>
        <button onClick={submitAudio} disabled={!audioBlob}>
          Submit Audio
        </button>
      </div>
      <audio ref={audioPlayerRef} controls />
      <div><p>Please wait a couple seconds after submitting the audio for processing time.</p></div>
      {transcription && (
        <div>
          <h2>Transcription:</h2>
          <p>{transcription}</p>
        </div>
      )}
      {imageUrl && (
        <div>
          <h2>Image:</h2>
          <img src={imageUrl} alt="Generated Image" />
        </div>
      )}
    </div>
  );
}

export default App;
