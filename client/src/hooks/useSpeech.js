import { useState, useEffect, useRef, useCallback } from 'react';

const useSpeech = () => {
    const [isListening, setIsListening] = useState(false);
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [transcript, setTranscript] = useState('');
    const recognitionRef = useRef(null);
    const synthesisRef = useRef(window.speechSynthesis);

    useEffect(() => {
        // Initialize Speech Recognition
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognitionRef.current = new SpeechRecognition();
            recognitionRef.current.continuous = false; // Stop after one sentence for turn-taking
            recognitionRef.current.interimResults = true;
            recognitionRef.current.lang = 'en-US';

            recognitionRef.current.onstart = () => setIsListening(true);
            recognitionRef.current.onend = () => setIsListening(false);

            recognitionRef.current.onresult = (event) => {
                let finalTranscript = '';
                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript;
                    }
                }
                if (finalTranscript) {
                    setTranscript(finalTranscript);
                }
            };

            recognitionRef.current.onerror = (event) => {
                console.error("Speech recognition error", event.error);
                setIsListening(false);
            };
        } else {
            console.warn("Speech Recognition not supported in this browser.");
        }

        return () => {
            if (recognitionRef.current) recognitionRef.current.stop();
            if (synthesisRef.current) synthesisRef.current.cancel();
        }
    }, []);

    const startListening = useCallback(() => {
        if (recognitionRef.current && !isListening) {
            setTranscript('');
            try {
                recognitionRef.current.start();
            } catch (e) {
                console.error("Error starting recognition:", e);
            }
        }
    }, [isListening]);

    const stopListening = useCallback(() => {
        if (recognitionRef.current && isListening) {
            recognitionRef.current.stop();
        }
    }, [isListening]);

    const speak = useCallback((text) => {
        if (!synthesisRef.current) return;

        // Cancel any current speaking
        synthesisRef.current.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.onstart = () => setIsSpeaking(true);
        utterance.onend = () => setIsSpeaking(false);
        utterance.onerror = (e) => {
            console.error("Speech synthesis error", e);
            setIsSpeaking(false);
        };

        // Optional: Select a better voice
        const voices = synthesisRef.current.getVoices();
        const preferredVoice = voices.find(v => v.name.includes("Google US English") || v.name.includes("Microsoft Zira"));
        if (preferredVoice) utterance.voice = preferredVoice;

        synthesisRef.current.speak(utterance);
    }, []);

    return {
        isListening,
        isSpeaking,
        transcript,
        startListening,
        stopListening,
        speak,
        hasSupport: !!recognitionRef.current
    };
};

export default useSpeech;
