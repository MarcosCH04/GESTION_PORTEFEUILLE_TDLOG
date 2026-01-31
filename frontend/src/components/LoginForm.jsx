// frontend/src/components/LoginForm.jsx
import React, { useState } from 'react';
import { authRequest } from '../api';

function LoginForm({ onSuccessfulLogin }) {
    // Form input states and UI feedback states
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    /* Handle form submission, validate inputs
     * Call authRequest() to authenticate, on success notify parent component
     * On error, display error message
     */
    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        // Validation: Check if fields are filled
        if (!username || !password) {
            setError("Please enter your username and password.");
            setLoading(false);
            return;
        }

        try {
            // Send login request to backend
            await authRequest('login', { username, password });
            onSuccessfulLogin(true);
        } catch (err) {

            // Display error from backend or fallback message
            console.error('Login error:', err);
            setError(err.message || 'Invalid username or password.');
        } finally {
            // Always stop loading spinner (success or error)
            setLoading(false);
        }
    };

    return (
        <div className="max-w-md w-full">
            <div className="bg-white rounded-2xl shadow-2xl p-8">
                {/* Form Header */}
                <div className="text-center mb-8">
                    <h2 className="text-3xl font-bold text-gray-900 mb-2">Welcome Back</h2>
                    <p className="text-gray-600">Log in to your account</p>
                </div>

                {/* Login Form */}
                <form onSubmit={handleSubmit} className="space-y-6">
                    
                    {/* Username Input */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Username
                        </label>
                        <input
                            type="text"
                            placeholder="Enter your username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className="w-full px-4 py-3 border border-gray-300 rounded-xl 
                                     focus:ring-2 focus:ring-primary-500 focus:border-transparent 
                                     transition-all duration-200 outline-none"
                            disabled={loading}
                        />
                    </div>

                    {/* Password Input */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Password
                        </label>
                        <input
                            type="password"
                            placeholder="Enter your password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full px-4 py-3 border border-gray-300 rounded-xl 
                                     focus:ring-2 focus:ring-primary-500 focus:border-transparent 
                                     transition-all duration-200 outline-none"
                            disabled={loading}
                        />
                    </div>

                    {/* Error Message Display */}
                    {error && (
                        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl">
                            {error}
                        </div>
                    )}

                    {/* Submit Button */}
                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-primary-500 text-white font-semibold py-3 rounded-xl 
                                 hover:bg-primary-600 transform hover:scale-105 
                                 transition-all duration-200 shadow-lg hover:shadow-xl
                                 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                    >
                        {loading ? 'Logging in...' : 'Log In'}
                    </button>
                </form>
            </div>
        </div>
    );
}

export default LoginForm;