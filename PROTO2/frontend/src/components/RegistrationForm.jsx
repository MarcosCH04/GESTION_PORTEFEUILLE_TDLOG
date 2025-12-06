import React, { useState } from 'react';
import { authRequest } from '../api';

function RegistrationForm({ onSuccessfulRegister }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setMessage('');

        if (!username || !password) {
            setError("Please fill in both fields.");
            return;
        }

        try {
            await authRequest('register', { username, password });
            setMessage('Registration successful! Redirecting to login...');
            
            // Call parent function to redirect/show success
            setTimeout(() => onSuccessfulRegister(), 1500); 

        } catch (err) {
            console.error('Registration error:', err);
            setError(err.message || 'An unexpected error occurred during registration.');
        }
    };

    return (
        <div className="auth-container">
            <h2>Register</h2>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
                <button type="submit">Register</button>
            </form>

            {error && <p className="error">{error}</p>}
            {message && <p className="success">{message}</p>}
        </div>
    );
}

export default RegistrationForm;