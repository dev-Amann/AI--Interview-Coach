import React, { useState } from 'react';
import Editor from "@monaco-editor/react";
import { ArrowLeft, Play, Code, RefreshCw, Wand2, Loader2, CheckCircle, AlertTriangle, Lightbulb } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const MockCoding = () => {
    const navigate = useNavigate();

    // Configuration State
    const [language, setLanguage] = useState('python');
    const [topic, setTopic] = useState('Arrays');
    const [difficulty, setDifficulty] = useState('Easy');

    // Problem & Editor State
    const [problem, setProblem] = useState(null);
    const [code, setCode] = useState("# Click 'Generate Problem' to start...");
    const [isGenerating, setIsGenerating] = useState(false);

    // Review State
    const [review, setReview] = useState(null);
    const [isReviewing, setIsReviewing] = useState(false);

    const languages = [
        { id: 'python', name: 'Python' },
        { id: 'javascript', name: 'JavaScript' },
        { id: 'java', name: 'Java' },
        { id: 'cpp', name: 'C++' }
    ];

    const topics = [
        'Arrays', 'Strings', 'Linked Lists', 'Trees', 'Graphs',
        'Dynamic Programming', 'Recursion', 'Sorting', 'Searching'
    ];

    const difficulties = ['Easy', 'Medium', 'Hard'];

    const handleGenerateProblem = async () => {
        setIsGenerating(true);
        setReview(null);
        try {
            const response = await api.post('/interview/coding/problem', {
                language,
                topic,
                difficulty
            });
            if (!response.data) throw new Error("Empty response");
            setProblem(response.data);
            setCode(response.data.starter_code || "");
        } catch (error) {
            console.error("Error generating problem:", error);
            alert("Failed to generate problem. Please try again.");
        } finally {
            setIsGenerating(false);
        }
    };

    const handleSubmitCode = async () => {
        if (!problem) return;

        setIsReviewing(true);
        try {
            const response = await api.post('/interview/coding/review', {
                code,
                problem_description: problem.description,
                language
            });
            setReview(response.data);
        } catch (error) {
            console.error("Error reviewing code:", error);
            alert("Failed to review code. Please try again.");
        } finally {
            setIsReviewing(false);
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
                            <Code className="w-6 h-6 text-indigo-600" /> Mock Coding Interview
                        </h1>
                    </div>
                </div>

                {/* Controls */}
                <div className="flex items-center gap-3">
                    <select
                        value={language}
                        onChange={(e) => setLanguage(e.target.value)}
                        className="px-3 py-2 rounded-lg border border-gray-300 text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
                    >
                        {languages.map(l => <option key={l.id} value={l.id}>{l.name}</option>)}
                    </select>

                    <select
                        value={topic}
                        onChange={(e) => setTopic(e.target.value)}
                        className="px-3 py-2 rounded-lg border border-gray-300 text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
                    >
                        {topics.map(t => <option key={t} value={t}>{t}</option>)}
                    </select>

                    <select
                        value={difficulty}
                        onChange={(e) => setDifficulty(e.target.value)}
                        className="px-3 py-2 rounded-lg border border-gray-300 text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
                    >
                        {difficulties.map(d => <option key={d} value={d}>{d}</option>)}
                    </select>

                    <button
                        onClick={handleGenerateProblem}
                        disabled={isGenerating}
                        className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-70"
                    >
                        {isGenerating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Wand2 className="w-4 h-4" />}
                        Generate Problem
                    </button>
                </div>
            </header>

            {/* Main Layout */}
            <div className="flex flex-1 overflow-hidden">
                {/* Left Panel: Problem & Review */}
                <div className="w-2/5 p-6 overflow-y-auto border-r border-gray-200 bg-white">
                    {!problem ? (
                        <div className="h-full flex flex-col items-center justify-center text-gray-400">
                            <Code className="w-16 h-16 mb-4 opacity-20" />
                            <p className="text-lg">Select options and click "Generate Problem" to start.</p>
                        </div>
                    ) : (
                        <div className="space-y-6">
                            {/* Problem Statement */}
                            <div className="prose prose-indigo max-w-none">
                                <h2 className="text-2xl font-bold text-gray-900 mb-2">{problem.title}</h2>
                                <div className="flex gap-2 mb-4">
                                    <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs font-medium">{language}</span>
                                    <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs font-medium">{topic}</span>
                                    <span className={`px-2 py-1 rounded text-xs font-medium ${difficulty === 'Easy' ? 'bg-green-100 text-green-700' :
                                        difficulty === 'Medium' ? 'bg-yellow-100 text-yellow-700' :
                                            'bg-red-100 text-red-700'
                                        }`}>{difficulty}</span>
                                </div>
                                <div className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                                    {problem.description}
                                </div>
                            </div>

                            {/* Review Section */}
                            {review && (
                                <div className={`mt-8 p-6 rounded-xl border-2 ${review.is_correct ? 'border-green-100 bg-green-50' : 'border-amber-100 bg-amber-50'}`}>
                                    <div className="flex items-center gap-3 mb-4">
                                        {review.is_correct ? (
                                            <CheckCircle className="w-6 h-6 text-green-600" />
                                        ) : (
                                            <AlertTriangle className="w-6 h-6 text-amber-600" />
                                        )}
                                        <h3 className={`text-lg font-bold ${review.is_correct ? 'text-green-800' : 'text-amber-800'}`}>
                                            {review.is_correct ? 'Correct Solution!' : 'Needs Improvement'}
                                        </h3>
                                    </div>

                                    <p className="text-gray-700 mb-4">{review.feedback}</p>

                                    {review.bugs && review.bugs.length > 0 && (
                                        <div className="mb-4">
                                            <h4 className="font-semibold text-gray-900 mb-2">Bugs & Issues:</h4>
                                            <ul className="list-disc list-inside space-y-1 text-gray-700">
                                                {review.bugs.map((bug, i) => <li key={i}>{bug}</li>)}
                                            </ul>
                                        </div>
                                    )}

                                    {review.optimization_tips && review.optimization_tips.length > 0 && (
                                        <div className="mb-4">
                                            <h4 className="font-semibold text-gray-900 flex items-center gap-2 mb-2">
                                                <Lightbulb className="w-4 h-4 text-yellow-500" /> Optimization Tips:
                                            </h4>
                                            <ul className="list-disc list-inside space-y-1 text-gray-700">
                                                {review.optimization_tips.map((tip, i) => <li key={i}>{tip}</li>)}
                                            </ul>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {/* Right Panel: Editor */}
                <div className="w-3/5 flex flex-col bg-gray-900">
                    <div className="flex items-center justify-between px-4 py-2 bg-gray-800 text-gray-300 text-xs border-b border-gray-700">
                        <span>main.{language === 'python' ? 'py' : language === 'javascript' ? 'js' : language === 'java' ? 'java' : 'cpp'}</span>
                        <span>Monaco Editor</span>
                    </div>
                    <div className="flex-1">
                        <Editor
                            height="100%"
                            language={language.toLowerCase() === 'c++' ? 'cpp' : language.toLowerCase()}
                            value={code}
                            onChange={(value) => setCode(value)}
                            theme="vs-dark"
                            options={{
                                minimap: { enabled: false },
                                fontSize: 14,
                                padding: { top: 16 },
                                scrollBeyondLastLine: false,
                            }}
                        />
                    </div>
                    <div className="p-4 bg-gray-800 border-t border-gray-700 flex justify-between items-center">
                        <button
                            onClick={() => setCode(problem?.starter_code || "")}
                            className="text-gray-400 hover:text-white flex items-center gap-2 text-sm transition-colors"
                            title="Reset Code"
                        >
                            <RefreshCw className="w-4 h-4" /> Reset
                        </button>
                        <button
                            onClick={handleSubmitCode}
                            disabled={isReviewing || !problem}
                            className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isReviewing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                            Run & Submit
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MockCoding;
