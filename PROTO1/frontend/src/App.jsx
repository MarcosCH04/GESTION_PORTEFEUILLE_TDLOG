// frontend/src/App.jsx

import React, { useEffect, useState } from "react";
import axios from "axios";
import AssetSelector from "./components/AssetSelector";
import PeriodSelector from "./components/PeriodSelector";
import StrategyForm from "./components/StrategyForm";
import PortfolioTable from "./components/PortfolioTable";
import Charts from "./components/Charts";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

function App() {
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

  const [assetPrices, setAssetPrices] = useState(null);   // pour le graphe des actifs
  const [metrics, setMetrics] = useState(null);           // pour le tableau
  const [portfolio, setPortfolio] = useState(null);       // pour le graphe du portefeuille

  const [error, setError] = useState("");

  // Récupération de la liste des actifs au chargement
  useEffect(() => {
    axios
      .get(`${API}/assets`)
      .then((res) => {
        setAssets(res.data.assets);
      })
      .catch((err) => {
        console.error(err);
        setError("Impossible de récupérer la liste des actifs.");
      });
  }, []);

  async function loadAssetData() {
    setError("");
    setPortfolio(null); // on efface l'ancien backtest
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
      const res = await axios.post(`${API}/analyze`, payload);
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
      const res = await axios.post(`${API}/backtest`, payload);
      setPortfolio(res.data.portfolio);
      setMetrics(res.data.metrics); // on met à jour les métriques (c'est cohérent)
    } catch (e) {
      console.error(e);
      setError("Erreur lors du backtest.");
    }
  }

  return (
    <div className="app-container">
      <h1>Investment Backtester (prototype)</h1>

      {error && <p style={{ color: "red" }}>{error}</p>}

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
