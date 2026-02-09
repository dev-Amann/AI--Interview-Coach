import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { Mic, Send, AlertCircle, CheckCircle, ArrowRight, Loader2 } from 'lucide-react';

const Interview = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { questions, user_name, config } = location.state || { questions: [], user_name: 'Candidate', config: {} };

    const [currentIndex, setCurrentIndex] = useState(0);
    const [answer, setAnswer] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [feedback, setFeedback] = useState(null);

    // Session State
    const [sessionData, setSessionData] = useState({
        answers: {},
        scores: [],
        feedback_list: [],
        ideal_answers_list: []
    });

    if (!questions || questions.length === 0) {
        return <div className="p-10 text-center">No questions loaded. Please restart setup.</div>;
    }

    const currentQuestion = questions[currentIndex];
    const progress = ((currentIndex) / questions.length) * 100;

    const handleSubmitAnswer = async () => {
        if (!answer.trim()) return;

        setIsSubmitting(true);
        try {
            const response = await api.post('/interview/answer', {
                question: currentQuestion,
                answer: answer,
                job_role: config.jobRole
            });

            const result = response.data;

            if (!result) throw new Error("Empty response");

            // Update session data
            setSessionData(prev => ({
                answers: { ...prev.answers, [currentIndex]: answer },
                scores: [...prev.scores, (result.score || 0)],
                feedback_list: [...prev.feedback_list, (result.feedback || "No feedback")],
                ideal_answers_list: [...prev.ideal_answers_list, (result.ideal_answer || "N/A")]
            }));

            setFeedback(result);
        } catch (error) {
            console.error("Error submitting answer:", error);
            alert("Failed to evaluate answer. Please try again.");
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleNext = () => {
        setFeedback(null);
        setAnswer('');

        if (currentIndex < questions.length - 1) {
            setCurrentIndex(prev => prev + 1);
        } else {
            finishInterview();
        }
    };

    const finishInterview = () => {
        // Navigate to results with all data
        navigate('/results', {
            state: {
                ...config, // jobRole, category, etc.
                questions: questions,
                answers: sessionData.answers,
                scores: sessionData.scores,
                feedback_list: sessionData.feedback_list,
                ideal_answers_list: sessionData.ideal_answers_list
            }
        });
    };

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col items-center py-10 px-4">
            <div className="max-w-3xl w-full">

                {/* Progress Bar */}
                <div className="mb-8">
                    <div className="flex justify-between text-sm font-medium text-gray-500 mb-2">
                        <span>Question {currentIndex + 1} of {questions.length}</span>
                        <span>{Math.round(progress)}% Complete</span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-indigo-600 transition-all duration-500 ease-out"
                            style={{ width: `${((currentIndex + 1) / questions.length) * 100}%` }}
                        ></div>
                    </div>
                </div>

                {currentIndex === 0 && !feedback && (
                    <div className="mb-6 p-6 bg-white border border-indigo-100 rounded-2xl shadow-sm animate-in fade-in slide-in-from-top-4 duration-700">
                        <h3 className="text-2xl font-bold text-gray-900 mb-1">Hello {user_name}! 👋</h3>
                        <p className="text-gray-600">Let's start your {config.category.toLowerCase()} interview for the {config.jobRole} position.</p>
                    </div>
                )}

                {/* Question Card */}
                <div className="card mb-6">
                    <h2 className="text-xl font-semibold text-gray-900 mb-2">
                        Question {currentIndex + 1}
                    </h2>
                    <p className="text-lg text-gray-700 leading-relaxed">
                        {currentQuestion}
                    </p>
                </div>

                {/* Feedback Area (Visible after submission) */}
                {feedback && (
                    <div className="mb-6 space-y-4">
                        <div className="card border-l-4 border-l-indigo-500 bg-indigo-50/50">
                            <div className="flex justify-between items-center mb-2">
                                <h3 className="font-semibold text-indigo-900">AI Feedback</h3>
                                <span className="bg-white px-3 py-1 rounded-full text-sm font-bold shadow-sm border border-indigo-100">
                                    Score: {feedback.score}/10
                                </span>
                            </div>
                            <p className="text-gray-700 text-sm mb-3">{feedback.feedback}</p>
                            <div>
                                <span className="text-xs font-bold text-gray-500 uppercase tracking-wide">Ideal Answer</span>
                                <p className="text-gray-600 text-sm mt-1 bg-white p-3 rounded-lg border border-gray-200">
                                    {feedback.ideal_answer}
                                </p>
                            </div>
                        </div>

                        <button
                            onClick={handleNext}
                            className="btn-primary w-full py-3 flex items-center justify-center gap-2"
                        >
                            {currentIndex < questions.length - 1 ? 'Next Question' : 'Finish Interview'} <ArrowRight className="w-5 h-5" />
                        </button>
                    </div>
                )}

                {/* Answer Input (Hidden if feedback is shown) */}
                {!feedback && (
                    <div className="card">
                        <textarea
                            className="input-field min-h-[200px] resize-none mb-4 font-mono text-sm"
                            placeholder="Type your answer here..."
                            value={answer}
                            onChange={(e) => setAnswer(e.target.value)}
                        />

                        <div className="flex justify-between items-center">
                            <div></div>
                            <button
                                onClick={handleSubmitAnswer}
                                disabled={isSubmitting || !answer.trim()}
                                className="btn-primary flex items-center gap-2 pl-6 pr-6"
                            >
                                {isSubmitting ? <Loader2 className="w-5 h-5 animate-spin" /> : <><Send className="w-4 h-4" /> Submit Answer</>}
                            </button>
                        </div>
                    </div>
                )}

            </div>
        </div>
    );
};

export default Interview;
