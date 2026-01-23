import React, { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, Loader2, ArrowLeft, Paperclip } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const ChatInterview = () => {
    const navigate = useNavigate();
    const [messages, setMessages] = useState([
        { role: 'assistant', content: "Hello! I am your AI Interview Coach. I can conduct a mock interview, review your resume, or answer technical questions. How would you like to start?" }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);
    const fileInputRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('resume', file);

        setIsLoading(true);
        try {
            // Show upload status
            setMessages(prev => [...prev, { role: 'user', content: `📎 Uploading ${file.name}...` }]);

            const res = await api.post('/interview/chat/resume', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            // Add hidden system context (via user role for simplicity in this stateless chat, or ideally a separate 'system' role if backend handles it)
            // But here, we'll send it as a special user message that the AI interprets, OR we append it to history.
            // Let's rely on the AI's ability to see the history.

            // Actually, we need to send this context to the AI immediately to get a response.

            const contextMessage = { role: 'user', content: res.data.context }; // Hidden context

            // We want to trigger the AI to respond to this resume
            const updatedMessages = [...messages, contextMessage];

            const aiRes = await api.post('/interview/chat', { messages: updatedMessages });

            setMessages(prev => [
                ...prev.slice(0, -1), // Remove "Uploading..."
                { role: 'user', content: `📄 Resume Uploaded: ${file.name}` },
                { role: 'assistant', content: aiRes.data.response }
            ]);

        } catch (error) {
            console.error("Upload Error:", error);
            if (error.response) {
                console.error("Error Detail:", error.response.data);
            }
            setMessages(prev => [...prev, { role: 'assistant', content: error.response?.data?.error || "Failed to upload resume. Please try again." }]);
        } finally {
            setIsLoading(false);
            e.target.value = null; // Reset input
        }
    };

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMessage = { role: 'user', content: input };
        const newMessages = [...messages, userMessage];

        setMessages(newMessages);
        setInput('');
        setIsLoading(true);

        try {
            // Filter out purely UI-only messages if any (like "Uploading..."), 
            // though we handle that by replacing state.
            // Note: The context message from resume upload should be preserved in 'messages' state 
            // if we want the AI to remember it. 
            // In the handleFileUpload above, we didn't add the context message to the visible 'messages' state properly for history.
            // Let's fix that logic: We should probably store the context but hide it, OR just show "Resume Uploaded" 
            // and rely on the fact that we sent the text content. 
            // Wait, if we don't save the text content in 'messages' state, the NEXT turn will lose the resume context.
            // CORRECT APPROACH: We must save the full text in the state, but maybe render it differently?
            // Or just append it to the hidden history array.

            // Refined Logic: We will add the context message to state but use a flag to hide/collapse it?
            // For now, let's just append it. If it's too long, the UI might be cluttered. 
            // Better: 'context' messages are valid user messages. We can just keep them.

            const apiMessages = newMessages.map(m => ({
                role: m.role,
                content: m.content
            }));

            const response = await api.post('/interview/chat', {
                messages: apiMessages
            });

            const aiMessage = { role: 'assistant', content: response.data.response };
            setMessages(prev => [...prev, aiMessage]);

        } catch (error) {
            console.error("Chat Error:", error);
            setMessages(prev => [...prev, { role: 'assistant', content: "I'm having trouble connecting right now. Please try again." }]);
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

    return (
        <div className="flex flex-col h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white border-b border-gray-200 p-4 flex items-center shadow-sm z-10">
                <button
                    onClick={() => navigate('/dashboard')}
                    className="mr-4 p-2 rounded-full hover:bg-gray-100 transition-colors"
                >
                    <ArrowLeft className="w-5 h-5 text-gray-600" />
                </button>
                <div>
                    <h1 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                        <Bot className="w-6 h-6 text-indigo-600" /> AI Coach Chat
                    </h1>
                    <p className="text-xs text-gray-500">Ask me anything about your interview preparation</p>
                </div>
            </header>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
                {messages.map((msg, index) => (
                    <div
                        key={index}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div className={`flex max-w-[80%] sm:max-w-[70%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'} items-start gap-3`}>
                            {/* Avatar */}
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${msg.role === 'user' ? 'bg-gray-200' : 'bg-indigo-600'
                                }`}>
                                {msg.role === 'user' ? <User className="w-5 h-5 text-gray-600" /> : <Bot className="w-5 h-5 text-white" />}
                            </div>

                            {/* Message Bubble */}
                            <div className={`p-4 rounded-2xl shadow-sm text-sm leading-relaxed ${msg.role === 'user'
                                ? 'bg-white text-gray-900 rounded-tr-none border border-gray-100'
                                : 'bg-indigo-600 text-white rounded-tl-none'
                                }`}>
                                <p className="whitespace-pre-wrap">{msg.content}</p>
                            </div>
                        </div>
                    </div>
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

            {/* Input Area */}
            <div className="bg-white border-t border-gray-200 p-4">
                <div className="max-w-4xl mx-auto relative flex gap-2 items-center">
                    <input
                        type="file"
                        ref={fileInputRef}
                        onChange={handleFileUpload}
                        accept=".pdf,.jpg,.jpeg,.png"
                        className="hidden"
                    />
                    <button
                        onClick={() => fileInputRef.current?.click()}
                        disabled={isLoading}
                        className="p-3 bg-gray-100 text-gray-500 rounded-xl hover:bg-gray-200 transition-colors"
                        title="Upload Resume (PDF, JPG, PNG)"
                    >
                        <Paperclip className="w-5 h-5" />
                    </button>

                    <div className="relative flex-1">
                        <textarea
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyPress}
                            placeholder="Type a message..."
                            className="w-full pl-4 pr-12 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none resize-none h-[52px] max-h-32 shadow-sm bg-gray-50 focus:bg-white transition-colors"
                        />
                        <button
                            onClick={handleSend}
                            disabled={isLoading || !input.trim()}
                            className="absolute right-2 top-1.5 p-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <Send className="w-5 h-5" />
                        </button>
                    </div>
                </div>
                <p className="text-center text-xs text-gray-400 mt-2">
                    AI can make mistakes. Please check important information.
                </p>
            </div>
        </div>
    );
};

export default ChatInterview;
