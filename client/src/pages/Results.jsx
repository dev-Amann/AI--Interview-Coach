import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useUser } from '@clerk/clerk-react';
import api from '../services/api';
import { CheckCircle, AlertTriangle, Download, Home, Loader2 } from 'lucide-react';

const Results = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { user } = useUser();
    const state = location.state;

    const [isSaving, setIsSaving] = useState(true);
    const [saveError, setSaveError] = useState(null);

    if (!state) {
        return <div className="p-10">No result data found.</div>;
    }

    // Calculate stats
    const scores = state.scores || [];
    const avgScore = scores.length > 0 ? (scores.reduce((a, b) => a + b, 0) / scores.length) : 0;
    const isQualified = avgScore >= 6.5;

    const saveRef = React.useRef(false);

    useEffect(() => {
        const saveSession = async () => {
            if (saveRef.current) return;
            saveRef.current = true;

            try {
                await api.post('/interview/save', {
                    user_id: user.id,
                    email: user.emailAddresses[0].emailAddress,
                    name: user.fullName,
                    job_role: state.jobRole,
                    category: state.category,
                    difficulty: state.difficulty,
                    avg_score: avgScore,
                    qualified: isQualified,
                    questions: state.questions,
                    answers: state.answers,
                    scores: state.scores,
                    feedback_list: state.feedback_list,
                    ideal_answers_list: state.ideal_answers_list
                });
                setIsSaving(false);
            } catch (error) {
                console.error("Error saving session:", error);
                setSaveError("Failed to save results to history.");
                setIsSaving(false);
                // Allow retrying if needed, but for now strict prevention
            }
        };

        if (user) {
            saveSession();
        }
    }, [user, state]); // Added state to dependencies for correctness

    const handleDownload = async () => {
        try {
            const response = await api.post('/interview/report', {
                user_name: user?.fullName,
                job_role: state.jobRole,
                category: state.category,
                difficulty: state.difficulty,
                avg_score: avgScore,
                qualified: isQualified,
                questions: state.questions,
                answers: state.answers,
                scores: state.scores,
                feedback_list: state.feedback_list,
                ideal_answers_list: state.ideal_answers_list
            }, { responseType: 'blob' });

            // Create blob link to download
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'Interview_Report.pdf');
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            console.error("Download error:", err);
            alert("Failed to download PDF");
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 py-10 px-4">
            <div className="max-w-4xl mx-auto">

                {/* Header Card */}
                <div className="card text-center mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">Interview Complete</h1>
                    <p className="text-gray-500 mb-6">Here is how you performed</p>

                    <div className="flex justify-center items-center gap-4 mb-2">
                        <div className="text-6xl font-bold text-gray-900">
                            {avgScore.toFixed(1)}
                            <span className="text-2xl text-gray-400 font-normal">/10</span>
                        </div>
                    </div>

                    <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full font-medium mb-6 ${isQualified ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                        {isQualified ? <CheckCircle className="w-5 h-5" /> : <AlertTriangle className="w-5 h-5" />}
                        {isQualified ? 'Qualified' : 'Needs Improvement'}
                    </div>

                    <div className="flex justify-center gap-4">
                        <button
                            onClick={handleDownload}
                            className="btn-secondary flex items-center gap-2"
                        >
                            <Download className="w-5 h-5" /> Download Report
                        </button>
                        <button
                            onClick={() => navigate('/dashboard')}
                            className="btn-primary flex items-center gap-2"
                        >
                            <Home className="w-5 h-5" /> Back to Dashboard
                        </button>
                    </div>

                    {isSaving && <p className="text-xs text-gray-400 mt-4 flex items-center justify-center gap-2"><Loader2 className="w-3 h-3 animate-spin" /> Saving results...</p>}
                    {saveError && <p className="text-xs text-red-500 mt-4">{saveError}</p>}
                </div>

                {/* Detailed Review */}
                <div className="space-y-6">
                    <h2 className="text-xl font-bold text-gray-900 ml-1">Detailed Review</h2>

                    {state.questions.map((q, idx) => (
                        <div key={idx} className="card">
                            <div className="flex justify-between items-start mb-4">
                                <h3 className="font-medium text-gray-900 text-lg">Question {idx + 1}</h3>
                                <span className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm font-semibold">
                                    Score: {state.scores[idx]}/10
                                </span>
                            </div>
                            <p className="text-gray-700 mb-4 font-medium">{q}</p>

                            <div className="grid md:grid-cols-2 gap-6">
                                <div className="bg-gray-50 p-4 rounded-lg border border-gray-100">
                                    <span className="text-xs font-bold text-gray-400 uppercase tracking-wide block mb-2">Your Answer</span>
                                    <p className="text-sm text-gray-600 whitespace-pre-wrap">{state.answers[idx] || "No answer provided"}</p>
                                </div>
                                <div className="bg-indigo-50/50 p-4 rounded-lg border border-indigo-50">
                                    <span className="text-xs font-bold text-indigo-400 uppercase tracking-wide block mb-2">AI Feedback</span>
                                    <p className="text-sm text-indigo-900 mb-3">{state.feedback_list[idx]}</p>
                                    <span className="text-xs font-bold text-gray-400 uppercase tracking-wide block mb-1">Ideal Answer</span>
                                    <p className="text-xs text-gray-500 italic">{state.ideal_answers_list[idx]}</p>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

            </div>
        </div>
    );
};

export default Results;
