// — courbes des actifs + portefeuille
// On affiche :
// un premier graphique pour les actifs (si les données sont là),
// un second pour la valeur du portefeuille (si on a fait le backtest).

// Chemin d'accès:
// frontend/src/components/Charts.jsx

import React from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  Legend,
  Tooltip,
} from "chart.js";

ChartJS.register(LineElement, CategoryScale, LinearScale, Legend, Tooltip);

function buildAssetChartData(assetPrices) {
  if (!assetPrices) return null;

  const dates = Object.keys(assetPrices).sort();
  if (dates.length === 0) return null;

  const firstDate = dates[0];
  const assets = Object.keys(assetPrices[firstDate]);

  const datasets = assets.map((asset) => ({
    label: asset,
    data: dates.map((d) => assetPrices[d][asset]),
    fill: false,
  }));

  return {
    labels: dates,
    datasets,
  };
}

function buildPortfolioChartData(portfolio) {
  if (!portfolio) return null;

  const dates = Object.keys(portfolio).sort();
  const data = dates.map((d) => portfolio[d]);

  return {
    labels: dates,
    datasets: [
      {
        label: "Valeur du portefeuille",
        data,
        fill: false,
      },
    ],
  };
}

function Charts({ assetPrices, portfolio }) {
  const assetData = buildAssetChartData(assetPrices);
  const portfolioData = buildPortfolioChartData(portfolio);

  return (
    <div className="section">
      {assetData && (
        <>
          <h2>Courbes des actifs sélectionnés</h2>
          <Line data={assetData} />
        </>
      )}
      {portfolioData && (
        <>
          <h2>Évolution de la valeur du portefeuille</h2>
          <Line data={portfolioData} />
        </>
      )}
    </div>
  );
}

export default Charts;
