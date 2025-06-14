import React, { useEffect, useRef, useState } from 'react';

function SpeechToText({ onTranscript, onRecordingStatusChange, shouldStartRecording, onSpeechError }) {
  const recognitionRef = useRef(null);
  const silenceTimeoutRef = useRef(null);
  const [isListening, setIsListening] = useState(false);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      onSpeechError('Speech Recognition is not supported in this browser. Please use Chrome or Edge.');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setIsListening(true);
      onRecordingStatusChange(true);
      onSpeechError('');
      resetSilenceTimeout(); // Start 20s timer
    };

    recognition.onresult = (event) => {
      clearSilenceTimeout(); // Reset timer
      const transcript = event.results[0][0].transcript;
      onTranscript(transcript);

      // Automatically restart recognition to allow user to keep speaking
      restartRecognition();
    };

    recognition.onerror = (event) => {
      let message = 'Speech recognition error.';
      if (event.error === 'not-allowed') message = 'Microphone access denied.';
      else if (event.error === 'no-speech') message = 'No speech detected.';
      else if (event.error === 'audio-capture') message = 'Microphone not available.';
      else if (event.error === 'network') message = 'Network error.';
      onSpeechError(message);
      stopRecognition();
    };

    recognition.onend = () => {
      setIsListening(false);
      onRecordingStatusChange(false);
    };

    recognitionRef.current = recognition;

    return () => {
      stopRecognition();
    };
  }, []);

  useEffect(() => {
    if (shouldStartRecording && !isListening) {
      try {
        recognitionRef.current?.start();
      } catch (err) {
        onSpeechError(`Could not start microphone: ${err.message}`);
        onRecordingStatusChange(false);
      }
    } else if (!shouldStartRecording && isListening) {
      stopRecognition();
    }
  }, [shouldStartRecording]);

  function stopRecognition() {
    clearSilenceTimeout();
    recognitionRef.current?.stop();
  }

  function restartRecognition() {
    try {
      recognitionRef.current?.stop(); // Required before restart
      setTimeout(() => {
        if (shouldStartRecording) recognitionRef.current?.start();
      }, 200); // Slight delay to allow restart
    } catch (err) {
      onSpeechError(`Error restarting recognition: ${err.message}`);
    }
  }

  function resetSilenceTimeout() {
    clearSilenceTimeout();
    silenceTimeoutRef.current = setTimeout(() => {
      onSpeechError('Recording stopped after 20 seconds of silence.');
      stopRecognition();
    }, 20000);
  }

  function clearSilenceTimeout() {
    if (silenceTimeoutRef.current) {
      clearTimeout(silenceTimeoutRef.current);
      silenceTimeoutRef.current = null;
    }
  }

  return null;
}

export default SpeechToText;
