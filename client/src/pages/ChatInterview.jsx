import React, { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, Loader2, ArrowLeft, Paperclip, Mic, MicOff, Volume2, VolumeX, Video, VideoOff, Camera, AlertTriangle, StopCircle, CheckCircle, TrendingUp, Award } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import api from '../services/api';
import VideoPreview from '../components/VideoPreview';
import useSpeech from '../hooks/useSpeech';

const ChatInterview = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const { mode, config, resumeFile } = location.state || {};

    const [messages, setMessages] = useState([
        { role: 'assistant', content: "Hello! I am your AI Interview Coach. I can conduct a mock interview, review your resume, or answer technical questions. How would you like to start?" }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    // Feature Toggles
    const [isVoiceMode, setIsVoiceMode] = useState(false);
    const [isVideoMode, setIsVideoMode] = useState(false);
    const [behaviorAlerts, setBehaviorAlerts] = useState([]);

    // Analysis Results
    const [showResults, setShowResults] = useState(false);
    const [analysisData, setAnalysisData] = useState(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);

    useEffect(() => { console.log("ChatInterview Component Mounted"); }, []);

    const messagesEndRef = useRef(null);
    const fileInputRef = useRef(null);
    const { isListening, isSpeaking, transcript, startListening, stopListening, speak, hasSupport } = useSpeech();

    // Auto-Initialisation from Setup
    useEffect(() => {
        if (mode === 'real') {
            setIsVideoMode(true);
            setIsVoiceMode(true);

            // Allow time for components to mount before auto-uploading
            if (resumeFile) {
                handleAutoUpload(resumeFile, config);
            }
        }
    }, [mode, resumeFile, config]); // Added dependencies for useEffect

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, behaviorAlerts]);

    // Voice Interaction Logic
    const wasListeningRef = useRef(false);

    useEffect(() => {
        if (transcript) {
            setInput(transcript);
        }
    }, [transcript]);

    // Track listening state changes (no auto-send - user clicks send button)
    useEffect(() => {
        wasListeningRef.current = isListening;
    }, [isListening]);

    const handleSendVoice = async (text) => {
        if (!text.trim() || isLoading) return;

        const userMessage = { role: 'user', content: text };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const apiMessages = [...messages, userMessage].map(m => ({
                role: m.role,
                content: m.content
            }));

            const response = await api.post('/interview/chat', { messages: apiMessages });
            const aiMessage = { role: 'assistant', content: response.data.response };
            setMessages(prev => [...prev, aiMessage]);

            // Auto-speak the response in Real mode
            speak(response.data.response);
        } catch (error) {
            console.error("Chat Error:", error);
            setMessages(prev => [...prev, { role: 'assistant', content: "I'm having trouble connecting right now." }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleAutoUpload = async (file, configData) => {
        setIsLoading(true);
        try {
            setMessages(prev => [...prev, { role: 'user', content: `📎 Auto-Uploading Resume: ${file.name}...` }]);

            const formData = new FormData();
            formData.append('resume', file);
            if (configData) {
                formData.append('job_role', configData.jobRole);
                formData.append('difficulty', configData.difficulty);
            }

            const res = await api.post('/interview/chat/resume', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            const contextMessage = { role: 'user', content: res.data.context };
            const updatedMessages = [...messages, contextMessage];

            const aiRes = await api.post('/interview/chat', { messages: updatedMessages });

            setMessages(prev => [
                ...prev.slice(0, -1),
                { role: 'user', content: `📄 Resume Uploaded. Starting Real-Time Interview...` },
                { role: 'assistant', content: aiRes.data.response }
            ]);

            // Auto Speak initial response if in real mode
            if (mode === 'real') {
                // Small delay to ensure voice acts after state update
                setTimeout(() => speak(aiRes.data.response), 500);
            }

        } catch (error) {
            console.error("Auto Upload Error:", error);
            setMessages(prev => [...prev, { role: 'assistant', content: "Failed to process restart. Please try uploading manually." }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('resume', file);
        // Include config if available even in manual upload
        if (config) {
            formData.append('job_role', config.jobRole);
            formData.append('difficulty', config.difficulty);
        }

        setIsLoading(true);
        try {
            setMessages(prev => [...prev, { role: 'user', content: `📎 Uploading ${file.name}...` }]);

            const res = await api.post('/interview/chat/resume', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            const contextMessage = { role: 'user', content: res.data.context };
            const updatedMessages = [...messages, contextMessage];

            const aiRes = await api.post('/interview/chat', { messages: updatedMessages });

            setMessages(prev => [
                ...prev.slice(0, -1),
                { role: 'user', content: `📄 Resume Uploaded: ${file.name}` },
                { role: 'assistant', content: aiRes.data.response }
            ]);

            if (isVoiceMode) speak(aiRes.data.response);

        } catch (error) {
            console.error("Upload Error:", error);
            setMessages(prev => [...prev, { role: 'assistant', content: "Failed to upload resume. Please try again." }]);
        } finally {
            setIsLoading(false);
            e.target.value = null;
        }
    };

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMessage = { role: 'user', content: input };

        // Inject latest behavior alert if exists
        let finalMessages = [...messages, userMessage];
        if (behaviorAlerts.length > 0) {
            const lastAlert = behaviorAlerts[behaviorAlerts.length - 1];
            // Clear alerts after sending to avoid spamming context
            setBehaviorAlerts([]);
            // Add system note as a hidden user message or special context
            // ideally backend handles system messages, but here we append to history for context
            finalMessages.splice(finalMessages.length - 1, 0, {
                role: 'system',
                content: `[SYSTEM ALERT: ${lastAlert.message}]`
            });
        }

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const apiMessages = finalMessages.map(m => ({
                role: m.role,
                content: m.content
            }));

            const response = await api.post('/interview/chat', {
                messages: apiMessages
            });

            const aiMessage = { role: 'assistant', content: response.data.response };
            setMessages(prev => [...prev, aiMessage]);

            if (isVoiceMode) {
                speak(response.data.response);
            }

        } catch (error) {
            console.error("Chat Error:", error);
            setMessages(prev => [...prev, { role: 'assistant', content: "I'm having trouble connecting right now." }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const toggleVoiceMode = () => {
        setIsVoiceMode(!isVoiceMode);
        if (!isVoiceMode) {
            // Enabling voice
        } else {
            stopListening();
        }
    };

    const handleBehaviorAlert = (alert) => {
        // Debounce or limit alerts
        setBehaviorAlerts(prev => {
            if (prev.length > 0 && prev[prev.length - 1].message === alert) return prev;
            return [...prev, { message: alert, time: new Date() }];
        });
    };

    const handleEndInterview = async () => {
        setIsAnalyzing(true);
        stopListening();

        try {
            const response = await api.post('/interview/analyze', {
                conversation: messages,
                behavioral_alerts: behaviorAlerts,
                job_role: config?.jobRole || 'Software Developer',
                difficulty: config?.difficulty || 'Medium',
                user_name: config?.userName || 'Candidate'
            });

            if (response.data.success) {
                setAnalysisData(response.data.analysis);
                setShowResults(true);
            } else {
                alert("Failed to analyze interview. Please try again.");
            }
        } catch (error) {
            console.error("Analysis Error:", error);
            alert("Error analyzing interview. Please check your connection.");
        } finally {
            setIsAnalyzing(false);
        }
    };

    return (
        <div className="flex flex-col h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white border-b border-gray-200 p-4 flex items-center justify-between shadow-sm z-10">
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => navigate('/dashboard')}
                        className="p-2 rounded-full hover:bg-gray-100 transition-colors"
                    >
                        <ArrowLeft className="w-5 h-5 text-gray-600" />
                    </button>
                    <div>
                        <h1 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                            <Bot className="w-6 h-6 text-indigo-600" /> AI Coach
                            {isVoiceMode && <span className="text-xs bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full">Voice Active</span>}
                        </h1>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    <button
                        onClick={() => setIsVideoMode(!isVideoMode)}
                        className={`p-2 rounded-full transition-colors ${isVideoMode ? 'bg-indigo-100 text-indigo-600' : 'bg-gray-100 text-gray-500'}`}
                        title="Toggle Camera"
                    >
                        {isVideoMode ? <Video className="w-5 h-5" /> : <VideoOff className="w-5 h-5" />}
                    </button>
                    <button
                        onClick={toggleVoiceMode}
                        className={`p-2 rounded-full transition-colors ${isVoiceMode ? 'bg-indigo-100 text-indigo-600' : 'bg-gray-100 text-gray-500'}`}
                        title="Toggle Voice Mode"
                    >
                        {isVoiceMode ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
                    </button>

                    {/* End Interview Button */}
                    {mode === 'real' && messages.length > 2 && (
                        <button
                            onClick={handleEndInterview}
                            disabled={isAnalyzing}
                            className="ml-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center gap-2 text-sm font-medium disabled:opacity-50"
                        >
                            {isAnalyzing ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" /> Analyzing...
                                </>
                            ) : (
                                <>
                                    <StopCircle className="w-4 h-4" /> End Interview
                                </>
                            )}
                        </button>
                    )}
                </div>
            </header>

            <div className="flex flex-1 overflow-hidden">
                {/* Main Chat Area */}
                <div className={`flex-1 flex flex-col transition-all duration-300 ${isVideoMode ? 'w-2/3' : 'w-full'}`}>
                    <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
                        {messages.map((msg, index) => (
                            msg.role !== 'system' && (
                                <div
                                    key={index}
                                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                >
                                    <div className={`flex max-w-[80%] sm:max-w-[70%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'} items-start gap-3`}>
                                        <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${msg.role === 'user' ? 'bg-gray-200' : 'bg-indigo-600'}`}>
                                            {msg.role === 'user' ? <User className="w-5 h-5 text-gray-600" /> : <Bot className="w-5 h-5 text-white" />}
                                        </div>
                                        <div className={`p-4 rounded-2xl shadow-sm text-sm leading-relaxed ${msg.role === 'user'
                                            ? 'bg-white text-gray-900 rounded-tr-none border border-gray-100'
                                            : 'bg-indigo-600 text-white rounded-tl-none'
                                            }`}>
                                            <p className="whitespace-pre-wrap">{msg.content}</p>
                                        </div>
                                    </div>
                                </div>
                            )
                        ))}
                        {isLoading && (
                            <div className="flex justify-start">
                                <div className="flex items-center gap-3">
                                    <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center">
                                        <Bot className="w-5 h-5 text-white" />
                                    </div>
                                    <div className="bg-gray-100 px-4 py-2 rounded-2xl rounded-tl-none">
                                        <Loader2 className="w-5 h-5 animate-spin text-gray-500" />
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Answer Input (Hidden if feedback is shown OR in Real Mode) */}
                    {!isLoading && mode !== 'real' && (
                        <div className="bg-white border-t border-gray-200 p-4">
                            <div className="max-w-4xl mx-auto relative flex items-center gap-2">

                                <button className="p-2 text-gray-400 hover:text-indigo-600 transition-colors">
                                    <Paperclip className="w-5 h-5" />
                                </button>

                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    accept=".pdf,.doc,.docx,.txt"
                                    className="hidden"
                                    onChange={handleFileUpload}
                                />

                                <div className="flex-1 relative">
                                    <textarea
                                        value={input}
                                        onChange={(e) => setInput(e.target.value)}
                                        // onKeyPress={handleKeyPress} // Optional: Add enter to send
                                        placeholder={isListening ? "Listening..." : "Type your message..."}
                                        className="w-full bg-gray-100 border-0 rounded-xl px-4 py-3 pr-10 focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all resize-none max-h-32 text-gray-700 placeholder-gray-400"
                                        rows="1"
                                    />
                                    <div className="absolute right-2 top-1/2 -translate-y-1/2">
                                        {/* Voice Mode Toggle Trigger inside input (optional) */}
                                    </div>
                                </div>

                                <button
                                    onClick={isListening ? stopListening : startListening}
                                    className={`p-3 rounded-xl transition-all ${isListening ? 'bg-red-50 text-red-600 animate-pulse' : 'bg-gray-100 text-gray-500 hover:bg-indigo-50 hover:text-indigo-600'}`}
                                >
                                    {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                                </button>

                                <button
                                    onClick={handleSend}
                                    disabled={!input.trim() || isLoading}
                                    className="p-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md shadow-indigo-200"
                                >
                                    <Send className="w-5 h-5" />
                                </button>
                            </div>
                            <div className="text-center mt-2">
                                <p className="text-xs text-gray-400">AI can make mistakes. Please verify important information.</p>
                            </div>
                        </div>
                    )}

                    {/* Voice Control for Real Mode */}
                    {mode === 'real' && (
                        <div className="bg-white border-t border-gray-200 p-6 flex flex-col items-center justify-center gap-4">
                            <div className="text-center space-y-1">
                                <h3 className="font-semibold text-gray-900">Voice Interface Active</h3>
                                <p className="text-sm text-gray-500">Click mic to record, then send your message.</p>
                            </div>

                            {/* Transcript Display */}
                            {input && (
                                <div className="w-full max-w-md bg-gray-100 rounded-lg p-3 text-sm text-gray-700">
                                    "{input}"
                                </div>
                            )}

                            <div className="flex items-center gap-4">
                                {/* Mic Button */}
                                <button
                                    onClick={isListening ? stopListening : startListening}
                                    className={`w-16 h-16 rounded-full flex items-center justify-center transition-all shadow-lg ${isListening ? 'bg-red-500 text-white animate-pulse ring-4 ring-red-200' : 'bg-indigo-600 text-white hover:bg-indigo-700 ring-4 ring-indigo-100'}`}
                                    title={isListening ? "Stop Recording" : "Start Recording"}
                                >
                                    {isListening ? <MicOff className="w-8 h-8" /> : <Mic className="w-8 h-8" />}
                                </button>

                                {/* Send Button - appears when there's text */}
                                {input && !isListening && (
                                    <button
                                        onClick={() => handleSendVoice(input)}
                                        disabled={isLoading}
                                        className="w-14 h-14 rounded-full flex items-center justify-center bg-green-500 text-white hover:bg-green-600 transition-all shadow-lg ring-4 ring-green-100 disabled:opacity-50"
                                        title="Send Message"
                                    >
                                        {isLoading ? <Loader2 className="w-7 h-7 animate-spin" /> : <Send className="w-7 h-7" />}
                                    </button>
                                )}
                            </div>
                            <p className="text-xs text-gray-400 mt-2">{isListening ? "🎙 Recording..." : (input ? "Click green button to send" : "Click mic to start")}</p>
                        </div>
                    )}
                </div>

                {/* Right Side Video Panel */}
                {isVideoMode && (
                    <div className="w-1/3 bg-gray-900 border-l border-gray-800 flex flex-col">
                        <div className="p-4 border-b border-gray-800">
                            <h2 className="text-white font-semibold flex items-center gap-2">
                                <Camera className="w-5 h-5" /> Live Analysis
                            </h2>
                        </div>
                        <div className="p-4 flex-1 overflow-y-auto">
                            <VideoPreview onBehaviorAlert={handleBehaviorAlert} />

                            {/* Alert Log */}
                            <div className="mt-6">
                                <h3 className="text-gray-400 text-xs uppercase tracking-wider font-semibold mb-3">Behavior Events</h3>
                                <div className="space-y-2">
                                    {behaviorAlerts.length === 0 ? (
                                        <p className="text-gray-600 text-sm italic">No alerts detected yet.</p>
                                    ) : (
                                        behaviorAlerts.slice().reverse().map((alert, idx) => (
                                            <div key={idx} className="flex items-start gap-2 text-sm text-yellow-500 bg-yellow-500/10 p-2 rounded">
                                                <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                                                <span>{alert.message}</span>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Results Modal */}
            {showResults && analysisData && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
                        {/* Modal Header */}
                        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-6 text-white rounded-t-2xl">
                            <div className="flex items-center justify-between">
                                <div>
                                    <h2 className="text-2xl font-bold flex items-center gap-2">
                                        <Award className="w-7 h-7" /> Interview Analysis
                                    </h2>
                                    <p className="text-indigo-100 mt-1">Your performance breakdown</p>
                                </div>
                                <div className="text-center">
                                    <div className="text-4xl font-bold">{analysisData.overall_score || 75}</div>
                                    <div className="text-xs text-indigo-200">Overall Score</div>
                                </div>
                            </div>
                        </div>

                        {/* Scores Grid */}
                        <div className="p-6 grid grid-cols-2 md:grid-cols-4 gap-4 border-b">
                            <div className="text-center p-3 bg-blue-50 rounded-xl">
                                <div className="text-2xl font-bold text-blue-600">{analysisData.communication_score || '--'}</div>
                                <div className="text-xs text-gray-500">Communication</div>
                            </div>
                            <div className="text-center p-3 bg-green-50 rounded-xl">
                                <div className="text-2xl font-bold text-green-600">{analysisData.technical_score || '--'}</div>
                                <div className="text-xs text-gray-500">Technical</div>
                            </div>
                            <div className="text-center p-3 bg-purple-50 rounded-xl">
                                <div className="text-2xl font-bold text-purple-600">{analysisData.confidence_score || '--'}</div>
                                <div className="text-xs text-gray-500">Confidence</div>
                            </div>
                            <div className="text-center p-3 bg-orange-50 rounded-xl">
                                <div className="text-2xl font-bold text-orange-600">{analysisData.body_language_score || '--'}</div>
                                <div className="text-xs text-gray-500">Body Language</div>
                            </div>
                        </div>

                        {/* Verdict */}
                        <div className="p-6 border-b">
                            <div className={`text-center py-3 px-6 rounded-full inline-block font-semibold ${analysisData.verdict?.includes('EXCELLENT') ? 'bg-green-100 text-green-700' :
                                analysisData.verdict?.includes('READY') ? 'bg-blue-100 text-blue-700' :
                                    'bg-yellow-100 text-yellow-700'
                                }`}>
                                {analysisData.verdict || 'NEEDS PRACTICE'}
                            </div>
                        </div>

                        {/* Detailed Feedback */}
                        <div className="p-6 border-b">
                            <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                                <TrendingUp className="w-5 h-5 text-indigo-600" /> Detailed Feedback
                            </h3>
                            <p className="text-gray-600 leading-relaxed whitespace-pre-wrap">
                                {analysisData.detailed_feedback || 'No detailed feedback available.'}
                            </p>
                        </div>

                        {/* Strengths & Improvements */}
                        <div className="p-6 grid md:grid-cols-2 gap-6 border-b">
                            <div>
                                <h3 className="font-semibold text-green-700 mb-3 flex items-center gap-2">
                                    <CheckCircle className="w-5 h-5" /> Strengths
                                </h3>
                                <ul className="space-y-2">
                                    {(analysisData.strengths || ['Good attempt']).map((s, i) => (
                                        <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
                                            <span className="text-green-500 mt-1">✓</span> {s}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                            <div>
                                <h3 className="font-semibold text-orange-700 mb-3 flex items-center gap-2">
                                    <AlertTriangle className="w-5 h-5" /> Areas to Improve
                                </h3>
                                <ul className="space-y-2">
                                    {(analysisData.areas_for_improvement || ['Keep practicing']).map((a, i) => (
                                        <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
                                            <span className="text-orange-500 mt-1">→</span> {a}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>

                        {/* Recommendations */}
                        {analysisData.recommendations && (
                            <div className="p-6 border-b">
                                <h3 className="font-semibold text-gray-900 mb-3">💡 Recommendations</h3>
                                <ul className="space-y-2">
                                    {analysisData.recommendations.map((r, i) => (
                                        <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
                                            <span className="text-indigo-500 font-bold">{i + 1}.</span> {r}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {/* Actions */}
                        <div className="p-6 flex gap-4 justify-center">
                            <button
                                onClick={() => navigate('/dashboard')}
                                className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                            >
                                Back to Dashboard
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ChatInterview;
