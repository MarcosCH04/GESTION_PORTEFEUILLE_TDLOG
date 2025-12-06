import React, { useState } from 'react';
import { authRequest } from '../api';

function LoginForm({ onSuccessfulLogin }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (!username || !password) {
            setError("Please enter your username and password.");
            return;
        }

        try {
            // NOTE: The 'credentials: include' setting in api.js 
            // ensures the HTTP-only cookie is RECEIVED by the browser.
            await authRequest('login', { username, password });
            
            // If the request succeeds, the browser now holds the session token.
            onSuccessfulLogin(true); // Notify parent component (App.jsx) to update state/route

        } catch (err) {
            console.error('Login error:', err);
            setError(err.message || 'Invalid username or password.');
        }
    };

    return (
        <div className="auth-container">
            <h2>Login</h2>
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
                <button type="submit">Login</button>
            </form>

            {error && <p className="error">{error}</p>}
        </div>
    );
}

export default LoginForm;