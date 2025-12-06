import React from 'react';

function HomePage({ setShowRegistration, setShowLogin }) {
    return (
        <div className="home-page-container">
            <h1>Welcome to the Investment Backtester</h1>
            <p>Analyze asset data and simulate portfolio strategies securely.</p>
            
            <div className="button-group">
                <button 
                    onClick={() => setShowLogin(true)} 
                    className="btn-primary"
                >
                    Log In
                </button>
                <button 
                    onClick={() => setShowRegistration(true)} 
                    className="btn-secondary"
                >
                    Register
                </button>
            </div>
            
            <p>Access requires registration or logging in.</p>
        </div>
    );
}

export default HomePage;