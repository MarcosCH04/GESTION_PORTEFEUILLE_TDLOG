// frontend/src/App.jsx

import React, { useEffect, useState } from "react";
import axios from "axios";
// --- New Imports for Authentication ---
import LoginForm from "./components/LoginForm"; 
import RegistrationForm from "./components/RegistrationForm";
import { authRequest } from "./api"; // Utility function for auth calls
// --- End New Imports ---

import AssetSelector from "./components/AssetSelector";
import PeriodSelector from "./components/PeriodSelector";
import StrategyForm from "./components/StrategyForm";
import PortfolioTable from "./components/PortfolioTable";
import Charts from "./components/Charts";

// VITE_API_URL should be set to http://backend:8000 (Docker service name)
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

function App() {
    // --- AUTHENTICATION STATE ---
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [showRegistration, setShowRegistration] = useState(false);
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

    // --- NEW: Function to check for active session (e.g., on reload) ---
    // This is a simple, stateless check. If a protected endpoint responds 200, we are logged in.
    const checkSession = async () => {
        try {
            // Use a lightweight protected endpoint (or a new /api/me if you create one)
            // If the user has a valid cookie, this call should succeed.
            await axios.get(`${API_BASE_URL}/assets`, { withCredentials: true });
            setIsAuthenticated(true);
        } catch (err) {
            // 401 Unauthorized, 403 Forbidden, or network error
            setIsAuthenticated(false);
        }
    };

    // --- NEW: Logout Function ---
    const handleLogout = async () => {
        try {
            // Call the backend endpoint to clear the session and delete the cookie
            await axios.post(`${API_BASE_URL}/logout`, {}, { withCredentials: true });
        } catch (err) {
            // Log the error but proceed with frontend state cleanup anyway
            console.error("Logout failed on server side:", err);
        } finally {
            setIsAuthenticated(false);
            // Optionally clear all sensitive state here
            setAssetPrices(null);
            setMetrics(null);
            setPortfolio(null);
        }
    };
    // -----------------------------


    // Récupération de la liste des actifs au chargement
    useEffect(() => {
        // If the user *might* be authenticated (i.e., they have a cookie), check the session
        checkSession();
        
        // --- Original Asset Fetch Logic (moved inside a function for clarity) ---
        const fetchAssets = () => {
            axios.get(`${API_BASE_URL}/assets`)
                .then((res) => {
                    setAssets(res.data.assets);
                })
                .catch((err) => {
                    console.error(err);
                    setError("Impossible de récupérer la liste des actifs.");
                });
        };
        fetchAssets(); // Always fetch assets as they are publicly visible
    }, []);
    
    // --- MODIFIED loadAssetData and runBacktest to require credentials ---
    // axios must be configured to send the session cookie on every request
    const axiosConfig = { withCredentials: true };

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
            // Note: /analyze is generally public, but we add config just in case it becomes protected.
            const res = await axios.post(`${API_BASE_URL}/analyze`, payload, axiosConfig);
            setAssetPrices(res.data.prices);
            setMetrics(res.data.metrics);
        } catch (e) {
            console.error(e);
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
            // CRUCIAL: Must include axiosConfig to send the session cookie!
            const res = await axios.post(`${API_BASE_URL}/backtest`, payload, axiosConfig);
            setPortfolio(res.data.portfolio);
            setMetrics(res.data.metrics); 
        } catch (e) {
            console.error(e);
            // Check for 401/403 errors indicating session expiration
            if (e.response && e.response.status === 401) {
                setError("Session expirée. Veuillez vous reconnecter.");
                setIsAuthenticated(false);
            } else {
                setError("Erreur lors du backtest.");
            }
        }
    }
    
    // --- 1. RENDERING THE AUTHENTICATION VIEW ---
    if (!isAuthenticated) {
        return (
            <div className="auth-page">
                <h1>Investment Backtester (prototype)</h1>
                {showRegistration ? (
                    <>
                        {/* The RegistrationForm redirects to login on success */}
                        <RegistrationForm onSuccessfulRegister={() => setShowRegistration(false)} />
                        <p>
                            Already registered? <button onClick={() => setShowRegistration(false)}>Login here</button>
                        </p>
                    </>
                ) : (
                    <>
                        {/* The LoginForm sets isAuthenticated to true on success */}
                        <LoginForm onSuccessfulLogin={() => setIsAuthenticated(true)} />
                        <p>
                            Don't have an account? <button onClick={() => setShowRegistration(true)}>Register now</button>
                        </p>
                    </>
                )}
            </div>
        );
    }
    
    // --- 2. RENDERING THE MAIN APPLICATION VIEW (IF AUTHENTICATED) ---
    return (
        <div className="app-container">
            <header className="app-header">
                <h1>Investment Backtester (prototype)</h1>
                <button onClick={handleLogout}>Déconnexion</button> {/* Logout Button */}
            </header>

            {error && <p style={{ color: "red" }}>{error}</p>}

            {/* All your existing components and logic go here */}
            {/* 1. Liste d'actifs + cases à cocher */}
            <AssetSelector
                assets={assets}
                selected={selected}
                setSelected={setSelected}
                weights={weights}
                setWeights={setWeights}
            />

            {/* 2. Période pour les courbes + métriques */}
            <PeriodSelector period={period} setPeriod={setPeriod} />

            {/* bouton pour charger les courbes & métriques */}
            <div className="section">
                <button onClick={loadAssetData}>Charger les données des actifs</button>
            </div>

            {/* 3. Graphe des actifs + 4. Tableau des métriques */}
            <Charts assetPrices={assetPrices} portfolio={portfolio} />
            <PortfolioTable selectedAssets={selected} metrics={metrics} />

            {/* 5. Montant à investir */}
            <div className="section">
                <h2>Montant total à investir</h2>
                <input
                    type="number"
                    value={amount}
                    onChange={(e) => setAmount(Number(e.target.value))}
                />
            </div>

            {/* 6-7-8. Répartition + stratégie + période d'investissement */}
            <StrategyForm strategy={strategy} setStrategy={setStrategy} />

            {/* 9. Bouton pour lancer la stratégie et afficher le graphe portefeuille */}
            <div className="section">
                <button onClick={runBacktest}>Lancer le backtest de portefeuille</button>
            </div>
        </div>
    );
}

export default App;