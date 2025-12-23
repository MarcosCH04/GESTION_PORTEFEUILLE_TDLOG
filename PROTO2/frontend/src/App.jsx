import React, { useEffect, useState } from "react";
import axios from "axios";

// --- Authentication Components & Utility ---
import LoginForm from "./components/LoginForm"; 
import RegistrationForm from "./components/RegistrationForm";
import { authRequest } from "./api"; 
// --- Main App Components ---
import HomePage from "./components/HomePage"; 
import AssetSelector from "./components/AssetSelector";
import PeriodSelector from "./components/PeriodSelector";
import StrategyForm from "./components/StrategyForm";
import PortfolioTable from "./components/PortfolioTable";
import Charts from "./components/Charts";

// VITE_API_URL should be set to http://backend:8000/api
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

// Configure Axios globally to send cookies with all requests
axios.defaults.withCredentials = true;

const VIEW_STATES = {
    HOME: 'home',
    LOGIN: 'login',
    REGISTER: 'register',
    MAIN_APP: 'main_app', 
};


function App() {
    // --- ROUTING & AUTH STATE ---
    const [currentView, setCurrentView] = useState(VIEW_STATES.HOME); 
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    // ----------------------------

    const [assets, setAssets] = useState([]);
    const [selected, setSelected] = useState([]);
    const [period, setPeriod] = useState({
        start: "2018-01-01",
        end: "2023-01-01",
    });
    const [amount, setAmount] = useState(10000);
    const [weights, setWeights] = useState({});
    const [strategy, setStrategy] = useState({
        type: "buy_and_hold",
        stratStart: "2020-01-01",
        stratEnd: "2023-01-01",
    });

    const [assetPrices, setAssetPrices] = useState(null); 
    const [metrics, setMetrics] = useState(null); 
    const [portfolio, setPortfolio] = useState(null); 
    const [error, setError] = useState("");

    // --- Authentication & View Handlers ---

    const handleLoginSuccess = () => {
        setIsAuthenticated(true);
        setCurrentView(VIEW_STATES.MAIN_APP); // Go to the main app on success
    };

    const handleRegisterSuccess = () => {
        setCurrentView(VIEW_STATES.LOGIN); // Go to login after successful registration
    };

    const handleLogout = async () => {
        try {
            // 1. Clear server session/cookie
            await axios.post(`${API_BASE_URL}/logout`, {});
        } catch (err) {
            console.error("Logout failed on server side, proceeding with frontend state cleanup:", err);
        } finally {
            // 2. Clear sensitive data and reset view state
            setIsAuthenticated(false);
            setCurrentView(VIEW_STATES.HOME); 
            setAssetPrices(null);
            setMetrics(null);
            setPortfolio(null);
            setError("");
        }
    };

    // --- API Call Functions ---

    async function loadAssetData() {
    setError("");
    setPortfolio(null); 
    if (selected.length === 0) {
        setError("Veuillez sélectionner au moins un actif.");
        return;
    }
    try {
        const payload = {
            assets: selected,
            start_date: period.start,
            end_date: period.end,
        };
        const res = await axios.post(`${API_BASE_URL}/analyze`, payload);
        
        // DEBUG: Check what actually comes back
        console.log("Analyze API Response:", res.data);

        // FIX: Ensure you are using .prices (as defined in your backend)
        setAssetPrices(res.data.prices); 
        setMetrics(res.data.metrics);
    } catch (e) {
        console.error("Analyze Error:", e);
        setError("Erreur lors du chargement des données d'actifs.");
    }
}

    async function runBacktest() {
        setError("");
        if (selected.length === 0) {
            setError("Veuillez sélectionner au moins un actif.");
            return;
        }

        const w = selected.map((s) => weights[s] ?? 0);
        const sumW = w.reduce((acc, x) => acc + x, 0);
        if (sumW <= 0) {
            setError("La somme des poids doit être > 0.");
            return;
        }

        try {
            const payload = {
                assets: selected,
                start_date: period.start,
                end_date: period.end,
                invest_amount: amount,
                weights: w,
                strategy: strategy.type,
                strat_start: strategy.stratStart,
                strat_end: strategy.stratEnd,
            };
            // This endpoint requires the session cookie
            const res = await axios.post(`${API_BASE_URL}/backtest`, payload);
            setPortfolio(res.data.portfolio);
            setMetrics(res.data.metrics); 
            setAssetPrices(res.data.asset_prices);
        } catch (e) {
            console.error(e);
            // Crucial: Handle session expiration (401 from protected route)
            if (e.response && e.response.status === 401) {
                setError("Session expirée. Veuillez vous reconnecter.");
                setIsAuthenticated(false);
                setCurrentView(VIEW_STATES.LOGIN); // Redirect to login
            } else {
                setError("Erreur lors du backtest.");
            }
        }
    }
    
    // --- Data Loading Effect ---
    // Fetch assets on mount, regardless of login status (as they are public)
    useEffect(() => {
        axios.get(`${API_BASE_URL}/assets`)
            .then((res) => setAssets(res.data.assets))
            .catch((err) => {
                console.error(err);
                setError("Impossible de récupérer la liste des actifs.");
            });
    }, []);

    
    // --- RENDER ROUTER ---
    
    // 1. Render Main App if authenticated
    if (isAuthenticated && currentView === VIEW_STATES.MAIN_APP) {
        return (
            <div className="app-container">
                <header className="app-header">
                    <h1>Investment Backtester (prototype)</h1>
                    <button onClick={handleLogout}>Déconnexion</button>
                </header>

                {error && <p style={{ color: "red" }}>{error}</p>}

                {/* Main components and logic moved here */}
                <AssetSelector
                    assets={assets}
                    selected={selected}
                    setSelected={setSelected}
                    weights={weights}
                    setWeights={setWeights}
                />

                <PeriodSelector period={period} setPeriod={setPeriod} />

                <div className="section">
                    <button onClick={loadAssetData}>Charger les données des actifs</button>
                </div>

                <Charts assetPrices={assetPrices} portfolio={portfolio} />
                <PortfolioTable selectedAssets={selected} metrics={metrics} />

                <div className="section">
                    <h2>Montant total à investir</h2>
                    <input
                        type="number"
                        value={amount}
                        onChange={(e) => setAmount(Number(e.target.value))}
                    />
                </div>

                <StrategyForm strategy={strategy} setStrategy={setStrategy} />

                <div className="section">
                    <button onClick={runBacktest}>Lancer le backtest de portefeuille</button>
                </div>
            </div>
        );
    }

    // 2. Render Auth Views based on state
    switch (currentView) {
        case VIEW_STATES.LOGIN:
            return (
                <div className="auth-page">
                    <LoginForm onSuccessfulLogin={handleLoginSuccess} />
                    <p>
                        Need an account? <button onClick={() => setCurrentView(VIEW_STATES.REGISTER)}>Register now</button>
                    </p>
                    <p><button onClick={() => setCurrentView(VIEW_STATES.HOME)}>Back to Home</button></p>
                </div>
            );
        case VIEW_STATES.REGISTER:
            return (
                <div className="auth-page">
                    <RegistrationForm onSuccessfulRegister={handleRegisterSuccess} />
                    <p>
                        Already registered? <button onClick={() => setCurrentView(VIEW_STATES.LOGIN)}>Login here</button>
                    </p>
                    <p><button onClick={() => setCurrentView(VIEW_STATES.HOME)}>Back to Home</button></p>
                </div>
            );
        case VIEW_STATES.HOME:
        default:
            return (
                <HomePage 
                    setShowLogin={() => setCurrentView(VIEW_STATES.LOGIN)}
                    setShowRegistration={() => setCurrentView(VIEW_STATES.REGISTER)}
                />
            );
    }
}

export default App;