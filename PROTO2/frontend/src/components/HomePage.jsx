// frontend/src/components/HomePage.jsx
import React from 'react';

function HomePage({ setShowLogin, setShowRegistration }) {
    return (
        <div className="min-h-screen gradient-bg flex items-center justify-center p-4">
            <div className="max-w-4xl w-full">
                {/* Card principale */}
                <div className="bg-white rounded-2xl shadow-2xl overflow-hidden">
                    <div className="p-12 text-center">
                        {/* Logo/Titre */}
                        <div className="mb-8">
                            <h1 className="text-5xl font-bold text-gray-900 mb-4">
                                InvestTrack
                            </h1>
                            <div className="w-20 h-1 bg-primary-500 mx-auto rounded-full"></div>
                        </div>

                        {/* Description */}
                        <p className="text-xl text-gray-600 mb-12 leading-relaxed max-w-2xl mx-auto">
                            Analyze asset data and simulate portfolio strategies securely.
                            Build, test, and optimize your investment strategies with powerful tools.
                        </p>

                        {/* Boutons d'action */}
                        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
                            <button 
                                onClick={() => setShowLogin()}
                                className="px-8 py-4 bg-primary-500 text-white font-semibold rounded-xl 
                                         hover:bg-primary-600 transform hover:scale-105 
                                         transition-all duration-200 shadow-lg hover:shadow-xl"
                            >
                                Log In
                            </button>
                            <button 
                                onClick={() => setShowRegistration()}
                                className="px-8 py-4 bg-white text-primary-500 font-semibold rounded-xl 
                                         border-2 border-primary-500 hover:bg-primary-50 
                                         transform hover:scale-105 transition-all duration-200"
                            >
                                Register
                            </button>
                        </div>

                        {/* Note */}
                        <p className="text-sm text-gray-500">
                            Access requires registration or logging in
                        </p>
                    </div>

                    {/* Section features (optionnel) */}
                    <div className="bg-gray-50 px-12 py-8 grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="text-center">
                            <h3 className="font-semibold text-gray-900 mb-1">Analysis</h3>
                            <p className="text-sm text-gray-600">Deep portfolio metrics</p>
                        </div>
                        <div className="text-center">
                            <h3 className="font-semibold text-gray-900 mb-1">Backtesting</h3>
                            <p className="text-sm text-gray-600">Test your strategies</p>
                        </div>
                        <div className="text-center">
                            <h3 className="font-semibold text-gray-900 mb-1">Secure</h3>
                            <p className="text-sm text-gray-600">Your data protected</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default HomePage;