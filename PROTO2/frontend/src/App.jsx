// frontend/src/App.jsx
import React, { useEffect, useState } from "react";
import axios from "axios";

// Authentication Components
import LoginForm from "./components/LoginForm"; 
import RegistrationForm from "./components/RegistrationForm";
import HomePage from "./components/HomePage"; 

// Main Application Components 
import AssetSelector from "./components/AssetSelector";
import WeightAllocator from "./components/WeightAllocator";
import PeriodSelector from "./components/PeriodSelector";
import StrategyForm from "./components/StrategyForm";
import PortfolioTable from "./components/PortfolioTable";
import Charts from "./components/Charts";
import SavedStrategiesList from "./components/SavedStrategiesList";
import Toast from "./components/Toast";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
axios.defaults.withCredentials = true;

const VIEW_STATES = {
    HOME: 'home',
    LOGIN: 'login',
    REGISTER: 'register',
    MAIN_APP: 'main_app', 
};

function App() {
    // --- Authentication State ---
    const [currentView, setCurrentView] = useState(VIEW_STATES.HOME); 
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    // --- Asset Selection ---
    const [assets, setAssets] = useState([]);
    const [selected, setSelected] = useState([]);
    const [weights, setWeights] = useState({});

    // --- Analysis Period ---
    const [period, setPeriod] = useState({
        start: "2018-01-01",
        end: "2023-01-01",
    });

    // --- Portfolio Configuration ---
    const [amount, setAmount] = useState(10000);
    
    // --- Strategy Configuration ---
    const [strategy, setStrategy] = useState({
        type: "buy_and_hold",
        stratStart: "2020-01-01",
        stratEnd: "2023-01-01",
    });

    // --- Results ---
    const [assetPrices, setAssetPrices] = useState(null); 
    const [metrics, setMetrics] = useState(null); 
    const [portfolio, setPortfolio] = useState(null); 
    
    // --- Toast Notification ---
    const [toast, setToast] = useState(null);

    // --- Saved Strategies ---
    const [savedStrats, setSavedStrats] = useState([]);

    // --- Toast Helper ---
    const showToast = (message, type = 'error') => {
        setToast({ message, type });
    };

    // --- Authentication Handlers ---
    const handleLoginSuccess = () => {
        setIsAuthenticated(true);
        setCurrentView(VIEW_STATES.MAIN_APP);
    };

    const handleRegisterSuccess = () => {
        setCurrentView(VIEW_STATES.LOGIN);
    };

    const handleLogout = async () => {
        try {
            await axios.post(`${API_BASE_URL}/logout`, {});
        } catch (err) {
            console.error("Logout error:", err);
        } finally {
            setIsAuthenticated(false);
            setCurrentView(VIEW_STATES.HOME);
            // Reset all state
            setSelected([]);
            setWeights({});
            setAmount(10000);
            setAssetPrices(null);
            setMetrics(null);
            setPortfolio(null);
            setSavedStrats([]);
        }
    };

    // --- Refresh Strategies ---
    const refreshStrategies = async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/strategies`);
            setSavedStrats(res.data);
        } catch (err) {
            console.error("Error fetching strategies:", err);
        }
    };

    useEffect(() => {
        if (isAuthenticated) {
            refreshStrategies();
        }
    }, [isAuthenticated]);

    // --- Load Asset Data ---
    async function loadAssetData() {
        if (selected.length === 0) {
            showToast("Please select at least one asset before loading data.");
            return;
        }

        try {
            const payload = {
                assets: selected,
                start_date: period.start,
                end_date: period.end,
            };
            const res = await axios.post(`${API_BASE_URL}/analyze`, payload);
            setAssetPrices(res.data.prices); 
            setMetrics(res.data.metrics);
            showToast("Asset data loaded successfully!", "success");
        } catch (e) {
            console.error("Analyze Error:", e);
            showToast("Failed to load asset data. Please try again.");
        }
    }

    // --- Run Backtest ---
    async function runBacktest() {
        // Validation
        if (selected.length === 0) {
            showToast("Please select at least one asset.");
            return;
        }

        const w = selected.map((s) => weights[s] || 0);
        const sumW = w.reduce((acc, x) => acc + x, 0);
        
        if (Math.abs(sumW - 1.0) > 0.01) {
            showToast(`Weight allocation must sum to 100%. Current total: ${(sumW * 100).toFixed(1)}%`);
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
            
            const res = await axios.post(`${API_BASE_URL}/backtest`, payload);
            setPortfolio(res.data.portfolio);
            setMetrics(res.data.metrics); 
            setAssetPrices(res.data.asset_prices);
            refreshStrategies();
            showToast("Backtest completed successfully!", "success");
        } catch (e) {
            console.error(e);
            if (e.response && e.response.status === 401) {
                showToast("Session expired. Please log in again.");
                setIsAuthenticated(false);
                setCurrentView(VIEW_STATES.LOGIN);
            } else {
                showToast("Backtest failed. Please check your inputs.");
            }
        }
    }

    // --- Save Strategy ---
    async function saveStrategy() {
        const input = window.prompt("Enter a name for this strategy:", "My Strategy");
        if (input === null) return;

        const finalName = input.trim() || `Strategy ${new Date().toLocaleDateString()}`;

        try {
            await axios.post(`${API_BASE_URL}/strategies/save-current`, { name: finalName });
            showToast("Strategy saved successfully!", "success");
            refreshStrategies();
        } catch (e) {
            showToast("Failed to save strategy: too many strategies or internal error.");
        }
    }


    // --- Load Saved Strategy ---
    const loadSavedParameters = async (params) => {
        // 1. Charger les paramètres
        setSelected(params.assets || []);
        setAmount(params.invest_amount || 10000);
        setPeriod({
            start: params.start_date || "2018-01-01",
            end: params.end_date || "2023-01-01",
        });
        setStrategy({
            type: params.strategy || "buy_and_hold",
            stratStart: params.strat_start || "2020-01-01",
            stratEnd: params.strat_end || "2023-01-01", 
        });
        
        const newWeights = {};
        if (params.assets && params.weights) {
            params.assets.forEach((asset, index) => {
                newWeights[asset] = params.weights[index] || 0;
            });
        }
        setWeights(newWeights);
        showToast("Strategy parameters loaded!", "success");
        


    };

    // --- Fetch Assets on Mount ---
    useEffect(() => {
        axios.get(`${API_BASE_URL}/assets`)
            .then((res) => setAssets(res.data.assets))
            .catch((err) => {
                console.error(err);
                showToast("Failed to load asset list.");
            });
    }, []);

    // --- Auto-distribute weights when assets change ---
    useEffect(() => {
        if (selected.length > 0) {
            const equalWeight = 1 / selected.length;
            const newWeights = {};
            selected.forEach(asset => {
                newWeights[asset] = equalWeight;
            });
            setWeights(newWeights);
        }
    }, [selected.length]);

    // --- MAIN APP VIEW ---
    if (isAuthenticated && currentView === VIEW_STATES.MAIN_APP) {
        return (
            <div className="min-h-screen bg-gray-50">
                {/* Toast Notification */}
                {toast && (
                    <Toast 
                        message={toast.message} 
                        type={toast.type}
                        onClose={() => setToast(null)}
                    />
                )}

                {/* Header */}
                <header className="bg-white shadow-sm sticky top-0 z-50">
                    <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
                        <h1 className="text-2xl font-bold text-gray-900">
                            Investment Backtester
                        </h1>
                        <button 
                            onClick={handleLogout}
                            className="px-4 py-2 bg-red-500 text-white rounded-lg 
                                     hover:bg-red-600 transition-colors"
                        >
                            Logout
                        </button>
                    </div>
                </header>

                {/* Main Content */}
                <main className="max-w-7xl mx-auto px-4 py-8">
                    {/* Step 1: Asset Selection */}
                    <AssetSelector
                        assets={assets}
                        selected={selected}
                        setSelected={setSelected}
                    />

                    {/* Step 2: Analysis Period */}
                    <PeriodSelector period={period} setPeriod={setPeriod} />

                    {/* Load Asset Data Button */}
                    <div className="mb-6">
                        <button 
                            onClick={loadAssetData}
                            className="w-full md:w-auto px-8 py-3 bg-blue-500 text-white font-semibold rounded-lg 
                                     hover:bg-blue-600 transition-colors shadow-md"
                        >
                            Load Asset Data
                        </button>
                    </div>

                    {/* Asset Charts */}
                    {assetPrices && (
                        <Charts assetPrices={assetPrices} portfolio={null} />
                    )}

                    {/* Metrics Table */}
                    <PortfolioTable selectedAssets={selected} metrics={metrics} />
                    
                    {/* Step 3: Weight Allocation */}
                    {selected.length > 0 && (
                        <WeightAllocator
                            selected={selected}
                            weights={weights}
                            setWeights={setWeights}
                        />
                    )}
                    
                    {/* Step 4: Strategy Configuration */}
                    <StrategyForm 
                        strategy={strategy} 
                        setStrategy={setStrategy}
                        amount={amount}
                        setAmount={setAmount}
                    />

                    {/* Run Backtest Button */}
                    <div className="mb-6">
                        <button 
                            onClick={runBacktest}
                            className="w-full md:w-auto px-8 py-3 bg-primary-500 text-white font-semibold rounded-lg 
                                     hover:bg-primary-600 transition-colors shadow-md"
                        >
                            Run Portfolio Backtest
                        </button>
                    </div>

                    {/* Portfolio Results */}
                    {portfolio && (
                        <div className="space-y-6">
                            <Charts assetPrices={null} portfolio={portfolio} />
                            
                            <div className="bg-white rounded-xl shadow-sm p-6">
                                <button 
                                    onClick={saveStrategy}
                                    className="px-6 py-3 bg-green-500 text-white font-semibold rounded-lg 
                                             hover:bg-green-600 transition-colors"
                                >
                                    Save This Strategy
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Saved Strategies */}
                    <SavedStrategiesList 
                        savedStrats={savedStrats} 
                        onRefresh={refreshStrategies} 
                        onLoadStrategy={loadSavedParameters} 
                    />
                </main>
            </div>
        );
    }

    // --- AUTHENTICATION VIEWS ---
    switch (currentView) {
        case VIEW_STATES.LOGIN:
            return (
                <div className="min-h-screen gradient-bg flex flex-col">
                    <div className="flex-1 flex items-center justify-center p-4">
                        <LoginForm onSuccessfulLogin={handleLoginSuccess} />
                    </div>
                    <div className="pb-8 text-center">
                        <p className="text-white mb-2">
                            Need an account?{' '}
                            <button 
                                onClick={() => setCurrentView(VIEW_STATES.REGISTER)}
                                className="underline hover:text-gray-200 transition-colors font-semibold"
                            >
                                Register now
                            </button>
                        </p>
                        <button 
                            onClick={() => setCurrentView(VIEW_STATES.HOME)}
                            className="text-white opacity-75 hover:opacity-100 transition-opacity"
                        >
                            ← Back to Home
                        </button>
                    </div>
                </div>
            );

        case VIEW_STATES.REGISTER:
            return (
                <div className="min-h-screen gradient-bg flex flex-col">
                    <div className="flex-1 flex items-center justify-center p-4">
                        <RegistrationForm onSuccessfulRegister={handleRegisterSuccess} />
                    </div>
                    <div className="pb-8 text-center">
                        <p className="text-white mb-2">
                            Already registered?{' '}
                            <button 
                                onClick={() => setCurrentView(VIEW_STATES.LOGIN)}
                                className="underline hover:text-gray-200 transition-colors font-semibold"
                            >
                                Login here
                            </button>
                        </p>
                        <button 
                            onClick={() => setCurrentView(VIEW_STATES.HOME)}
                            className="text-white opacity-75 hover:opacity-100 transition-opacity"
                        >
                            ← Back to Home
                        </button>
                    </div>
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