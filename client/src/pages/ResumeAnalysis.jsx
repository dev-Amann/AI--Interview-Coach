import React, { useState } from 'react';
import { useUser } from '@clerk/clerk-react';
import api from '../services/api';
import {
    Upload, FileText, CheckCircle, AlertTriangle, XCircle,
    BarChart2, Loader2, ArrowLeft, Briefcase
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import {
    Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
    ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell
} from 'recharts';

const ResumeAnalysis = () => {
    const { user } = useUser();
    const navigate = useNavigate();
    const [file, setFile] = useState(null);
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            setFile(selectedFile);
            setAnalysis(null);
            setError('');
        }
    };

    const handleAnalyze = async () => {
        if (!file) return;

        setLoading(true);
        setError('');

        const formData = new FormData();
        formData.append('resume', file);

        try {
            const response = await api.post('/interview/resume/analyze', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setAnalysis(response.data);
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.error || "Failed to analyze resume. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 pb-20">
            {/* Header */}
            <header className="bg-white border-b border-gray-200 p-4 sticky top-0 z-10 shadow-sm">
                <div className="max-w-7xl mx-auto flex items-center gap-4">
                    <button
                        onClick={() => navigate('/dashboard')}
                        className="p-2 rounded-full hover:bg-gray-100 transition-colors"
                    >
                        <ArrowLeft className="w-5 h-5 text-gray-600" />
                    </button>
                    <h1 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                        <FileText className="w-6 h-6 text-indigo-600" /> Resume Analyzer
                    </h1>
                </div>
            </header>

            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

                {/* Upload Section */}
                {!analysis && (
                    <div className="max-w-2xl mx-auto">
                        <div className="bg-white rounded-2xl shadow-sm p-8 text-center border-2 border-dashed border-gray-300 hover:border-indigo-500 transition-colors">
                            <div className="w-16 h-16 bg-indigo-50 rounded-full flex items-center justify-center mx-auto mb-4">
                                <Upload className="w-8 h-8 text-indigo-600" />
                            </div>
                            <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload your Resume</h2>
                            <p className="text-gray-500 mb-6">Supported formats: PDF, JPG, PNG (Max 5MB)</p>

                            <input
                                type="file"
                                id="resume-upload"
                                className="hidden"
                                accept=".pdf,.jpg,.jpeg,.png"
                                onChange={handleFileChange}
                            />

                            {!file ? (
                                <label
                                    htmlFor="resume-upload"
                                    className="btn-primary inline-flex items-center gap-2 cursor-pointer"
                                >
                                    Select File
                                </label>
                            ) : (
                                <div className="space-y-4">
                                    <div className="flex items-center justify-center gap-2 text-gray-700 font-medium bg-gray-50 p-3 rounded-lg">
                                        <FileText className="w-5 h-5 text-indigo-600" />
                                        {file.name}
                                    </div>
                                    <div className="flex gap-3 justify-center">
                                        <button
                                            onClick={() => setFile(null)}
                                            className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-800"
                                        >
                                            Change File
                                        </button>
                                        <button
                                            onClick={handleAnalyze}
                                            disabled={loading}
                                            className="btn-primary items-center gap-2 flex"
                                        >
                                            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <BarChart2 className="w-5 h-5" />}
                                            Analyze Now
                                        </button>
                                    </div>
                                </div>
                            )}

                            {error && (
                                <div className="mt-6 p-4 bg-red-50 text-red-700 rounded-xl flex items-center justify-center gap-2">
                                    <AlertTriangle className="w-5 h-5" />
                                    {error}
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Analysis Result */}
                {analysis && (
                    <div className="animate-fade-in space-y-8">

                        {/* Summary & Score */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            {/* Score Card */}
                            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-col items-center justify-center text-center">
                                <div className="relative w-32 h-32 flex items-center justify-center mb-4">
                                    <svg className="w-full h-full transform -rotate-90">
                                        <circle
                                            cx="64"
                                            cy="64"
                                            r="56"
                                            stroke="#f3f4f6"
                                            strokeWidth="12"
                                            fill="transparent"
                                        />
                                        <circle
                                            cx="64"
                                            cy="64"
                                            r="56"
                                            stroke={analysis.ats_score > 70 ? "#10b981" : analysis.ats_score > 40 ? "#f59e0b" : "#ef4444"}
                                            strokeWidth="12"
                                            fill="transparent"
                                            strokeDasharray={351.86}
                                            strokeDashoffset={351.86 - (351.86 * analysis.ats_score) / 100}
                                            className="transition-all duration-1000 ease-out"
                                        />
                                    </svg>
                                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                                        <span className="text-3xl font-bold text-gray-900">{analysis.ats_score}</span>
                                        <span className="text-xs text-gray-500 uppercase tracking-wider">ATS Score</span>
                                    </div>
                                </div>
                                <h3 className="text-lg font-bold text-gray-900">
                                    {analysis.ats_score > 80 ? 'Excellent!' : analysis.ats_score > 60 ? 'Good Start' : 'Needs Work'}
                                </h3>
                                <p className="text-sm text-gray-500 mt-1">Based on keyword matching & formatting</p>
                            </div>

                            {/* Summary Card */}
                            <div className="md:col-span-2 bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                                <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                                    <Briefcase className="w-5 h-5 text-indigo-600" /> Professional Summary
                                </h3>
                                <p className="text-gray-700 leading-relaxed mb-6">
                                    {analysis.summary}
                                </p>

                                <h4 className="text-sm font-semibold text-gray-900 mb-3">Suggested Roles for You:</h4>
                                <div className="flex flex-wrap gap-2">
                                    {analysis.suggested_roles.map((role, idx) => (
                                        <span key={idx} className="px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-sm font-medium">
                                            {role}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        </div>

                        {/* Details Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

                            {/* Strengths */}
                            <div className="bg-white p-6 rounded-2xl shadow-sm border-t-4 border-green-500">
                                <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                                    <CheckCircle className="w-5 h-5 text-green-600" /> Top Strengths
                                </h3>
                                <ul className="space-y-3">
                                    {analysis.strengths.map((item, idx) => (
                                        <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                                            <span className="w-1.5 h-1.5 bg-green-500 rounded-full mt-1.5 shrink-0" />
                                            {item}
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            {/* Weaknesses */}
                            <div className="bg-white p-6 rounded-2xl shadow-sm border-t-4 border-red-500">
                                <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                                    <AlertTriangle className="w-5 h-5 text-red-600" /> Critical Gaps
                                </h3>
                                <ul className="space-y-3">
                                    {analysis.weaknesses.map((item, idx) => (
                                        <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                                            <span className="w-1.5 h-1.5 bg-red-500 rounded-full mt-1.5 shrink-0" />
                                            {item}
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            {/* Missing Skills */}
                            <div className="bg-white p-6 rounded-2xl shadow-sm border-t-4 border-amber-500">
                                <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                                    <XCircle className="w-5 h-5 text-amber-600" /> Missing Keywords
                                </h3>
                                <div className="flex flex-wrap gap-2">
                                    {analysis.missing_skills.map((skill, idx) => (
                                        <span key={idx} className="px-2.5 py-1 bg-gray-100 text-gray-700 rounded-md text-xs font-medium border border-gray-200">
                                            {skill}
                                        </span>
                                    ))}
                                </div>
                                <p className="text-xs text-gray-400 mt-4">
                                    Adding these keywords can significantly improve your ATS ranking.
                                </p>
                            </div>
                        </div>

                        <div className="flex justify-center pt-8">
                            <button
                                onClick={() => { setAnalysis(null); setFile(null); }}
                                className="text-gray-500 hover:text-indigo-600 font-medium transition-colors"
                            >
                                Analyze Another Resume
                            </button>
                        </div>

                    </div>
                )}
            </main>
        </div>
    );
};

export default ResumeAnalysis;
