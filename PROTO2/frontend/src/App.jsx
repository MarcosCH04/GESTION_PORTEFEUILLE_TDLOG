// frontend/src/App.jsx

import React, { useEffect, useState } from "react";
import axios from "axios";

// Authentication Components and Utilities
import LoginForm from "./components/LoginForm"; 
import RegistrationForm from "./components/RegistrationForm";
import { authRequest } from "./api"; 
// Main Application Components 
import HomePage from "./components/HomePage"; 
import AssetSelector from "./components/AssetSelector";
import PeriodSelector from "./components/PeriodSelector";
import StrategyForm from "./components/StrategyForm";
import PortfolioTable from "./components/PortfolioTable";
import Charts from "./components/Charts";
import SavedStrategiesList from "./components/SavedStrategiesList";

// VITE_API_URL should be set to http://backend:8000/api
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

// Configure Axios globally to send cookies with all requests
axios.defaults.withCredentials = true;

// Application View States 
const VIEW_STATES = {
    HOME: 'home',
    LOGIN: 'login',
    REGISTER: 'register',
    MAIN_APP: 'main_app', 
};


function App() {
    // --- Authentication and View State ---
    const [currentView, setCurrentView] = useState(VIEW_STATES.HOME); 
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    // --- Asset Selection states ---
    const [assets, setAssets] = useState([]);
    const [selected, setSelected] = useState([]);

    // --- Analysis Period State
    const [period, setPeriod] = useState({
        start: "2018-01-01",
        end: "2023-01-01",
    });

    // --- Portfolio Configuration State ---
    const [amount, setAmount] = useState(10000);
    const [weights, setWeights] = useState({});
    
    // --- Strategy Configuration State ---
    const [strategy, setStrategy] = useState({
        type: "buy_and_hold",
        stratStart: "2020-01-01",
        stratEnd: "2023-01-01",
    });

    // --- User Saved Strategies --- 
    const [savedStrats, setSavedStrats] = useState([]);

    // --- Results and Error State ---
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

    // Helper function to reset application state on logout
    const resetForm = () => {
        setSelected([]);
        setAmount(10000);
        setWeights({});
        setPeriod({
            start: "2018-01-01",
            end: "2023-01-01",
        });
        setStrategy({
            type: "buy_and_hold",
            stratStart: "2020-01-01",
            stratEnd: "2023-01-01",
        });
        setAssetPrices(null);
        setMetrics(null);
        setPortfolio(null);
        setSavedStrats([]); // Clear the list of strategies
        setError("");
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
            resetForm();
        }
    };

    // --- Refresh Strategies Function ---

    const refreshStrategies = async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/strategies`);
            setSavedStrats(res.data);
        } catch (err) {
            console.error("Erreur actualisation list:", err);
        }
    };

    useEffect(() => {
        if (isAuthenticated) {
            refreshStrategies();
        }
    }, [isAuthenticated]);

    // --- API Call Functions ---

    /**
     * Loads historical price data and metrics for selected assets
     * This is a public endpoint (no authentication required)
     */
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
        
        console.log("Analyze API Response:", res.data);

        // Store price data and metrics from backend response
        setAssetPrices(res.data.prices); 
        setMetrics(res.data.metrics);

    } catch (e) {
        console.error("Analyze Error:", e);
        setError("Erreur lors du chargement des données d'actifs.");
    }
}
    /**
     * Runs portfolio backtest simulation
     * This is a protected endpoint (requires authentication)
     */
    async function runBacktest() {
        setError("");
        if (selected.length === 0) {
            setError("Veuillez sélectionner au moins un actif.");
            return;
        }

        // Build weights array matching selected assets order
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
            // Send authenticated request (uses session cookie)
            const res = await axios.post(`${API_BASE_URL}/backtest`, payload);
            
            // Store backtest results from backend response
            setPortfolio(res.data.portfolio);
            setMetrics(res.data.metrics); 
            setAssetPrices(res.data.asset_prices);

            // Refresh saved strategies list
            refreshStrategies();
        } catch (e) {
            console.error(e);
            // Handle session expiration (401 from protected route)
            if (e.response && e.response.status === 401) {
                setError("Session expirée. Veuillez vous reconnecter.");
                setIsAuthenticated(false);
                setCurrentView(VIEW_STATES.LOGIN); // Redirect to login
            } else {
                setError("Erreur lors du backtest.");
            }
        }
    }

    // --- Strategy Saving Function (Protected) ---
    async function saveStrategy() {
        setError("");
        
        // Prompt the user
        const input = window.prompt("Entrez un nom pour cette stratégie:", "Ma Stratégie");
        
        // If user clicks "Cancel", input is null. 
        if (input === null) return; 

        // Use input if not empty, otherwise fallback to a default
        const finalName = input.trim() || `Stratégie du ${new Date().toLocaleDateString()}`;

        try {
            await axios.post(`${API_BASE_URL}/strategies/save-current`, {
                name: finalName
            });
            alert("Stratégie enregistrée !");
            refreshStrategies();
        } catch (e) {
            setError("Erreur lors de la sauvegarde.");
        }
    }

    // --- Load Saved Strategy Parameters ---
    const loadSavedParameters = (params) => {
    // 1. Update Asset Selection
    setSelected(params.assets || []);

    // 2. Update Investment Amount
    setAmount(params.invest_amount || 10000);

    // 3. Update Analysis Period
    setPeriod({
        start: params.start_date || "2018-01-01",
        end: params.end_date || "2023-01-01",
    });

    // 4. Update Strategy Method & Simulation Dates
    // Note the mapping from snake_case (backend) to camelCase (frontend state)
    setStrategy({
        type: params.strategy || "buy_and_hold",
        stratStart: params.strat_start || "2020-01-01",
        stratEnd: params.strat_end || "2023-01-01", 
    });
    
    // 5. Update Weights Object
    const newWeights = {};
    if (params.assets && params.weights) {
        params.assets.forEach((asset, index) => {
            newWeights[asset] = params.weights[index] || 0;
        });
    }
    setWeights(newWeights);
    
    alert("Paramètres chargés ! Cliquez sur 'Lancer le backtest'.");
    };

    
    // --- Data Loading Effect ---
    // Fetch available assets on component mount (public endpoint)
    useEffect(() => {
        axios.get(`${API_BASE_URL}/assets`)
            .then((res) => setAssets(res.data.assets))
            .catch((err) => {
                console.error(err);
                setError("Impossible de récupérer la liste des actifs.");
            });
    }, []);

    
    // --- RENDER ROUTER ---
    
    // 1. Main application view (requires authentication)
 if (isAuthenticated && currentView === VIEW_STATES.MAIN_APP) {
    return (
        <div className="app-container">
            <header className="app-header">
                <h1>Investment Backtester (prototype)</h1>
                <button onClick={handleLogout}>Déconnexion</button>
            </header>

            {error && <p style={{ color: "red" }}>{error}</p>}

            {/* Asset selection with weight allocation */}
            <AssetSelector
                assets={assets}
                selected={selected}
                setSelected={setSelected}
                weights={weights}
                setWeights={setWeights}
            />

            {/* Historical data period selector */}
            <PeriodSelector period={period} setPeriod={setPeriod} />

            <div className="section">
                <button onClick={loadAssetData}>Charger les données des actifs</button>
            </div>

            {/* Asset price chart */}
            {assetPrices && (
                <Charts assetPrices={assetPrices} portfolio={null} />
            )}
            
            {/* Performance metrics table */}
            <PortfolioTable selectedAssets={selected} metrics={metrics} />

            {/* Investment amount input */}
            <div className="section">
                <h2>Montant total à investir</h2>
                <input
                    type="number"
                    value={amount}
                    onChange={(e) => setAmount(Number(e.target.value))}
                />
            </div>

            {/* Strategy configuration */}
            <StrategyForm strategy={strategy} setStrategy={setStrategy} />

            <div className="section">
                <button onClick={runBacktest}>Lancer le backtest de portefeuille</button>
            </div>

            {/* Portfolio chart */}
            {portfolio && (
                <>
                    <div className="section">
                        <h2>Performance du portefeuille (Valeur totale)</h2>
                        <Charts assetPrices={null} portfolio={portfolio} />
                    </div>
                    
                    <div className="section">
                        <button 
                            onClick={saveStrategy}
                            style={{ backgroundColor: '#22c55e', color: 'white' }}
                        >
                            Sauvegarder cette configuration
                        </button>
                    </div>
                </>
            )}

            {/* Saved Strategies List */}
            <SavedStrategiesList 
                savedStrats={savedStrats} 
                onRefresh={refreshStrategies} 
                onLoadStrategy={loadSavedParameters} 
            />
        </div>
    );
}

    // 2. Authentication and home views
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