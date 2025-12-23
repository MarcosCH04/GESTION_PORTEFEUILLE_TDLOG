import React, { useMemo } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Legend,
  Tooltip,
  Filler,
} from "chart.js";

ChartJS.register(LineElement, PointElement, CategoryScale, LinearScale, Legend, Tooltip, Filler);

const CHART_COLORS = [
    'rgb(255, 99, 132)', 'rgb(54, 162, 235)', 'rgb(255, 205, 86)', 
    'rgb(75, 192, 192)', 'rgb(153, 102, 255)', 'rgb(255, 159, 64)'
];

function Charts({ assetPrices, portfolio }) {
  // If no data at all, show the friendly placeholder
  if (!assetPrices && !portfolio) {
    return (
      <div className="section chart-container p-12 text-center border-2 border-dashed border-gray-200 rounded-lg">
        <p className="text-gray-500 italic">Sélectionnez des actifs et lancez l'analyse pour visualiser les courbes.</p>
      </div>
    );
  }

  // 1. Process Asset Curves
  const assetData = useMemo(() => {
    if (!assetPrices || Object.keys(assetPrices).length === 0) return null;
    const dates = Object.keys(assetPrices).sort();
    const assets = Object.keys(assetPrices[dates[0]]);

    return {
      labels: dates,
      datasets: assets.map((asset, index) => ({
        label: asset,
        data: dates.map(d => assetPrices[d][asset]),
        borderColor: CHART_COLORS[index % CHART_COLORS.length],
        backgroundColor: CHART_COLORS[index % CHART_COLORS.length],
        fill: false,
        tension: 0.1,
        pointRadius: 0,
        spanGaps: true,
      }))
    };
  }, [assetPrices]);

  // 2. Process Portfolio Area Chart
  const portfolioData = useMemo(() => {
    if (!portfolio || Object.keys(portfolio).length === 0) return null;
    const dates = Object.keys(portfolio).sort();

    return {
      labels: dates,
      datasets: [{
        label: "Valeur du portefeuille",
        data: dates.map(d => portfolio[d]),
        fill: true,
        backgroundColor: "rgba(34, 197, 94, 0.2)", // Light Green Fill
        borderColor: "rgb(34, 197, 94)",           // Solid Green Line
        tension: 0.2,
        pointRadius: 0,
        spanGaps: true,
      }]
    };
  }, [portfolio]);

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    plugins: {
      legend: { position: 'top' },
      tooltip: { mode: 'index', intersect: false }
    },
    scales: {
      x: { 
        ticks: { 
          maxTicksLimit: 10,
          color: '#888' 
        },
        grid: { display: false }
      },
      y: { 
        beginAtZero: false,
        ticks: { color: '#888' }
      }
    }
  };

  return (
    <div className="section chart-container space-y-12 my-8">
      {assetData && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold mb-4 text-gray-800">Évolution des prix des actifs</h3>
          <div style={{ height: '350px' }}>
            <Line data={assetData} options={options} />
          </div>
        </div>
      )}

      {portfolioData && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold mb-4 text-gray-800">Performance du portefeuille (Valeur totale)</h3>
          <div style={{ height: '350px' }}>
            <Line data={portfolioData} options={options} />
          </div>
        </div>
      )}
    </div>
  );
}

export default Charts;