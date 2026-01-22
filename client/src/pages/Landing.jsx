import React from 'react';
import { SignInButton, useUser, UserButton } from '@clerk/clerk-react';
import { Navigate } from 'react-router-dom';
import { ArrowRight, CheckCircle, Video, Mic, FileText } from 'lucide-react';
import { motion } from 'framer-motion';

const Landing = () => {
    const { isSignedIn, isLoaded } = useUser();

    if (!isLoaded) {
        return <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>;
    }

    if (isSignedIn) {
        return <Navigate to="/dashboard" replace />;
    }

    return (
        <div className="min-h-screen bg-gray-50 text-gray-900 font-sans selection:bg-indigo-100">
            {/* Navbar */}
            <nav className="fixed w-full z-50 glass border-b border-gray-200">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16 items-center">
                        <div className="flex items-center gap-2">
                            <div className="bg-indigo-600 p-2 rounded-lg">
                                <Mic className="w-5 h-5 text-white" />
                            </div>
                            <span className="font-bold text-xl tracking-tight">InterviewCoach.ai</span>
                        </div>
                        <div>
                            <SignInButton mode="modal">
                                <button className="text-sm font-medium text-gray-600 hover:text-indigo-600 transition-colors px-4 py-2">
                                    Sign In
                                </button>
                            </SignInButton>
                            <SignInButton mode="modal">
                                <button className="btn-primary ml-2 text-sm">
                                    Get Started
                                </button>
                            </SignInButton>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto text-center">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                >
                    <span className="inline-block px-4 py-1.5 rounded-full bg-indigo-50 text-indigo-700 text-sm font-medium mb-6 border border-indigo-100">
                        Now with AI-Powered Real-time Feedback
                    </span>
                    <h1 className="text-5xl sm:text-7xl font-bold tracking-tight mb-8 leading-tight text-gray-900">
                        Master Your Next <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">
                            Technical Interview
                        </span>
                    </h1>
                    <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-10 leading-relaxed">
                        Practice with our advanced AI coach that adapts to your resume and job role.
                        Get instant feedback on your answers, speech, and technical accuracy.
                    </p>

                    <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                        <SignInButton mode="modal">
                            <button className="btn-primary flex items-center gap-2 px-8 py-4 text-lg shadow-lg shadow-indigo-200">
                                Start Practicing Free <ArrowRight className="w-5 h-5" />
                            </button>
                        </SignInButton>
                        <a href="#how-it-works" className="btn-secondary px-8 py-4 text-lg">
                            how it works
                        </a>
                    </div>
                </motion.div>


            </section>

            {/* Features Grid */}
            <section id="features" className="py-20 bg-white border-t border-gray-100">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="grid md:grid-cols-3 gap-10">
                        {[
                            {
                                icon: <FileText className="w-6 h-6 text-indigo-600" />,
                                title: "Resume Parsing",
                                desc: "Our AI scans your resume to generate relevant, role-specific questions tailored to your experience."
                            },

                            {
                                icon: <CheckCircle className="w-6 h-6 text-indigo-600" />,
                                title: "Instant Scoring",
                                desc: "Receive detailed scores (0-10) and comprehensive feedback immediately after every answer."
                            }
                        ].map((feature, idx) => (
                            <div key={idx} className="p-8 rounded-2xl bg-gray-50 border border-gray-100 hover:shadow-lg transition-all duration-300">
                                <div className="w-12 h-12 bg-white rounded-xl shadow-sm flex items-center justify-center mb-6 border border-gray-100">
                                    {feature.icon}
                                </div>
                                <h3 className="text-xl font-bold mb-3 text-gray-900">{feature.title}</h3>
                                <p className="text-gray-600 leading-relaxed">
                                    {feature.desc}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-10 bg-gray-50 border-t border-gray-200">
                <div className="max-w-7xl mx-auto px-4 text-center text-gray-500 text-sm">
                    <p>© 2026 AI Interview Coach. Built by Team 2.</p>
                </div>
            </footer>
        </div>
    );
};

export default Landing;
