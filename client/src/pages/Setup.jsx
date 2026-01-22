import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '@clerk/clerk-react';
import api from '../services/api';
import { Upload, FileText, ArrowRight, Loader2 } from 'lucide-react';

const Setup = () => {
    const navigate = useNavigate();
    const [isLoading, setIsLoading] = useState(false);
    const [formData, setFormData] = useState({
        jobRole: 'Python Developer',
        category: 'Technical',
        difficulty: 'Medium',
        resumeFile: null
    });

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!formData.resumeFile) return;

        setIsLoading(true);
        try {
            const data = new FormData();
            data.append('resume_file', formData.resumeFile);
            data.append('job_role', formData.jobRole);
            data.append('category', formData.category);
            data.append('difficulty', formData.difficulty);

            const response = await api.post('/interview/start', data, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            // Navigate to interview with generated questions
            navigate('/interview', {
                state: {
                    questions: response.data.questions,
                    config: formData
                }
            });
        } catch (error) {
            console.error("Error generating questions:", error);
            alert("Failed to generate questions. Please try again.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
            <div className="max-w-2xl w-full">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Interview Setup</h1>
                    <p className="text-gray-500 mt-2">Configure your session and upload your resume.</p>
                </div>

                <div className="card">
                    <form onSubmit={handleSubmit} className="space-y-6">

                        {/* Job Role */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Target Role</label>
                            <select
                                className="input-field"
                                value={formData.jobRole}
                                onChange={(e) => setFormData({ ...formData, jobRole: e.target.value })}
                            >
                                {["Python Developer", "Data Scientist", "Web Developer", "DevOps Engineer", "Full Stack Developer", "AI Engineer"].map(role => (
                                    <option key={role} value={role}>{role}</option>
                                ))}
                            </select>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            {/* Category */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
                                <select
                                    className="input-field"
                                    value={formData.category}
                                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                                >
                                    <option value="Technical">Technical</option>
                                    <option value="Behavioral">Behavioral</option>
                                    <option value="HR">HR</option>
                                </select>
                            </div>

                            {/* Difficulty */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Difficulty</label>
                                <select
                                    className="input-field"
                                    value={formData.difficulty}
                                    onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}
                                >
                                    <option value="Easy">Easy</option>
                                    <option value="Medium">Medium</option>
                                    <option value="Hard">Hard</option>
                                </select>
                            </div>
                        </div>

                        {/* Resume Upload */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Upload Resume (PDF)
                            </label>
                            <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-lg hover:border-indigo-500 transition-colors bg-white/50">
                                <div className="space-y-1 text-center">
                                    <Upload className="mx-auto h-12 w-12 text-gray-400" />
                                    <div className="flex text-sm text-gray-600 justify-center">
                                        <label htmlFor="file-upload" className="relative cursor-pointer bg-white rounded-md font-medium text-indigo-600 hover:text-indigo-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500">
                                            <span>Upload a file</span>
                                            <input
                                                id="file-upload"
                                                name="file-upload"
                                                type="file"
                                                className="sr-only"
                                                accept=".pdf"
                                                onChange={(e) => setFormData({ ...formData, resumeFile: e.target.files[0] })}
                                            />
                                        </label>
                                        <p className="pl-1">or drag and drop</p>
                                    </div>
                                    <p className="text-xs text-gray-500">PDF up to 10MB</p>
                                    {formData.resumeFile && (
                                        <div className="flex items-center gap-2 text-sm text-green-600 justify-center mt-2 bg-green-50 py-1 px-3 rounded-full">
                                            <FileText className="w-4 h-4" />
                                            {formData.resumeFile.name}
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={isLoading || !formData.resumeFile}
                            className="btn-primary w-full flex items-center justify-center gap-2 py-3 text-lg"
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 className="w-5 h-5 animate-spin" /> Generating Questions...
                                </>
                            ) : (
                                <>
                                    Start Interview <ArrowRight className="w-5 h-5" />
                                </>
                            )}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default Setup;
