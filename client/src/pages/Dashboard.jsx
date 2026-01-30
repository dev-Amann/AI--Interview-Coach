import React, { useState, useEffect } from 'react';
import { useUser, useClerk } from '@clerk/clerk-react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import {
    LineChart, Plus, Clock, Award, TrendingUp, Calendar,
    ArrowRight, LogOut, Bot, FileText, Code
} from 'lucide-react';

const Dashboard = () => {
    const { user } = useUser();
    const { signOut } = useClerk();
    const navigate = useNavigate();
    const [stats, setStats] = useState(null);
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            if (!user) return;
            try {
                const [statsRes, historyRes] = await Promise.all([
                    api.get(`/user/stats/${user.id}`),
                    api.get(`/user/history/${user.id}`)
                ]);
                setStats(statsRes.data?.stats);
                setHistory(historyRes.data || []);
            } catch (error) {
                console.error("Error fetching dashboard data:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [user]);

    const handleStartInterview = () => {
        navigate('/setup');
    };

    const handleViewReport = async (sessionId) => {
        try {
            const response = await api.get(`/interview/report/${sessionId}`, {
                responseType: 'blob'
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `Interview_Report_${sessionId}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            console.error("Error downloading report:", error);
            alert("Failed to download report.");
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="animate-pulse flex flex-col items-center">
                    <div className="h-12 w-12 bg-gray-200 rounded-full mb-4"></div>
                    <div className="h-4 w-32 bg-gray-200 rounded"></div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 text-gray-900 pb-20">
            {/* Navbar */}
            <nav className="bg-white border-b border-gray-200 sticky top-0 z-10">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16 items-center">
                        <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate('/')}>
                            <div className="bg-indigo-600 p-1.5 rounded-lg">
                                <LineChart className="w-5 h-5 text-white" />
                            </div>
                            <span className="font-bold text-lg">InterviewCoach.ai</span>
                        </div>
                        <div className="flex items-center gap-4">
                            <span className="text-sm font-medium text-gray-700 hidden sm:block">
                                Welcome, {user?.firstName}
                            </span>
                            <button
                                onClick={() => signOut()}
                                className="text-gray-500 hover:text-red-600 transition-colors p-2 rounded-full hover:bg-gray-100"
                                title="Sign Out"
                            >
                                <LogOut className="w-5 h-5" />
                            </button>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

                {/* Header Section */}
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
                        <p className="text-gray-500 mt-1">Track your progress and start new sessions.</p>
                    </div>
                    <div className="flex gap-3">
                        <button
                            onClick={() => navigate('/resume-analysis')}
                            className="btn-secondary flex items-center gap-2"
                        >
                            <FileText className="w-5 h-5 text-indigo-600" /> Resume Analysis
                        </button>
                        <button
                            onClick={() => navigate('/mock-coding')}
                            className="btn-secondary flex items-center gap-2"
                        >
                            <Code className="w-5 h-5 text-indigo-600" /> Coding
                        </button>
                        <button
                            onClick={() => navigate('/chat')}
                            className="btn-secondary flex items-center gap-2"
                        >
                            <Bot className="w-5 h-5 text-indigo-600" /> Chat with Coach
                        </button>
                        <button
                            onClick={handleStartInterview}
                            className="btn-primary flex items-center gap-2 shadow-lg shadow-indigo-100"
                        >
                            <Plus className="w-5 h-5" /> Start New Interview
                        </button>
                    </div>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
                    <StatCard
                        icon={<Clock className="w-6 h-6 text-blue-600" />}
                        label="Total Sessions"
                        value={stats?.total_sessions || 0}
                        color="bg-blue-50"
                    />
                    <StatCard
                        icon={<TrendingUp className="w-6 h-6 text-green-600" />}
                        label="Average Score"
                        value={stats?.overall_avg_score ? Number(stats.overall_avg_score).toFixed(1) : "0.0"}
                        color="bg-green-50"
                    />
                    <StatCard
                        icon={<Award className="w-6 h-6 text-purple-600" />}
                        label="Highest Score"
                        value={stats?.best_score ? Number(stats.best_score).toFixed(1) : "0.0"}
                        color="bg-purple-50"
                    />
                    <StatCard
                        icon={<CheckCircle className="w-6 h-6 text-indigo-600" />} // Imported below
                        label="Qualified"
                        value={stats?.qualified_count || 0}
                        color="bg-indigo-50"
                    />
                </div>

                {/* Recent History Table */}
                <div className="card">
                    <div className="flex justify-between items-center mb-6">
                        <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                            <Calendar className="w-5 h-5 text-gray-400" /> Recent Interviews
                        </h3>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="text-gray-500 text-sm border-b border-gray-100">
                                    <th className="font-medium p-4 pl-0">Role</th>
                                    <th className="font-medium p-4">Date</th>
                                    <th className="font-medium p-4">Category</th>
                                    <th className="font-medium p-4">Score</th>
                                    <th className="font-medium p-4">Status</th>
                                    <th className="font-medium p-4 text-right">Action</th>
                                </tr>
                            </thead>
                            <tbody className="text-sm">
                                {history.length > 0 ? (
                                    history.map((session) => (
                                        <tr key={session.id} className="group hover:bg-gray-50 transition-colors border-b border-gray-50 last:border-0">
                                            <td className="p-4 pl-0 font-medium text-gray-900">{session.job_role}</td>
                                            <td className="p-4 text-gray-500">{new Date(session.created_at).toLocaleDateString()}</td>
                                            <td className="p-4 text-gray-600">
                                                <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                                                    {session.category || 'Technical'}
                                                </span>
                                            </td>
                                            <td className="p-4 font-semibold text-gray-900">{Number(session.avg_score).toFixed(1)}</td>
                                            <td className="p-4">
                                                <StatusBadge qualified={session.qualified} />
                                            </td>
                                            <td className="p-4 text-right">
                                                <button
                                                    onClick={() => handleViewReport(session.id)}
                                                    className="text-indigo-600 hover:text-indigo-800 font-medium text-xs flex items-center gap-1 justify-end ml-auto opacity-0 group-hover:opacity-100 transition-opacity"
                                                >
                                                    View Report <ArrowRight className="w-3 h-3" />
                                                </button>
                                            </td>
                                        </tr>
                                    ))
                                ) : (
                                    <tr>
                                        <td colSpan="6" className="p-8 text-center text-gray-500">
                                            No interviews yet. Start your first session!
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </main>
        </div>
    );
};

// Sub-components for cleaner code
const StatCard = ({ icon, label, value, color }) => (
    <div className="card flex items-center gap-4 hover:shadow-md transition-shadow">
        <div className={`p-3 rounded-xl ${color}`}>
            {icon}
        </div>
        <div>
            <p className="text-sm font-medium text-gray-500">{label}</p>
            <p className="text-2xl font-bold text-gray-900">{value}</p>
        </div>
    </div>
);

const StatusBadge = ({ qualified }) => {
    const isQualified = qualified === 1 || qualified === true;
    return (
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${isQualified ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
            }`}>
            {isQualified ? 'Qualified' : 'Improvement'}
        </span>
    );
};

import { CheckCircle } from 'lucide-react'; // Late import fix if needed

export default Dashboard;
