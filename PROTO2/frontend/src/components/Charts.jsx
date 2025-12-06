// — courbes des actifs + portefeuille
// FIX: Ajout de PointElement à l'enregistrement de Chart.js pour résoudre l'erreur "point is not a registered element".
// FIX: Ajout de couleurs distinctes aux datasets pour résoudre le problème de la ligne unique grise.
// CHANGE: L'ordre des graphiques est REVERTED: Actifs en premier, Portefeuille en second, pour que ce dernier soit plus bas sur la page.
// NOTE: Les hooks useMemo et useEffect sont maintenus pour optimiser la performance
// et éviter le blocage du thread principal par le rendu du graphique.

import React, { useMemo, useState, useEffect } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  PointElement, // <<< FIX: Component required to draw the points on the line graph
  CategoryScale,
  LinearScale,
  Legend,
  Tooltip,
} from "chart.js";

// L'enregistrement inclut maintenant PointElement pour éviter le crash
ChartJS.register(LineElement, PointElement, CategoryScale, LinearScale, Legend, Tooltip);


// --- Couleurs pour les graphiques ---
const CHART_COLORS = [
    'rgb(255, 99, 132)', // Rouge
    'rgb(54, 162, 235)', // Bleu
    'rgb(255, 205, 86)', // Jaune
    'rgb(75, 192, 192)', // Vert
    'rgb(153, 102, 255)',// Violet
    'rgb(255, 159, 64)', // Orange
    'rgb(201, 203, 207)',// Gris
];

// --- Fonctions de transformation de données (maintenues et optimisées par useMemo) ---

function buildAssetChartData(assetPrices) {
  if (!assetPrices) return null;

  const dates = Object.keys(assetPrices).sort();
  if (dates.length === 0) return null;

  const firstDate = dates[0];
  const assets = Object.keys(assetPrices[firstDate]);

  const datasets = assets.map((asset, index) => { // ⭐️ Use index here
    const color = CHART_COLORS[index % CHART_COLORS.length]; // Cycle through colors
    return {
      label: asset,
      data: dates.map((d) => assetPrices[d][asset]), 
      fill: false,
      tension: 0.1,
      pointRadius: 0, 
      borderColor: color, // ⭐️ Assigned unique border color
      backgroundColor: color, // ⭐️ Assigned unique background color
    };
  });

  return {
    labels: dates,
    datasets,
  };
}

function buildPortfolioChartData(portfolio) {
  if (!portfolio) return null;

  const dates = Object.keys(portfolio).sort();
  const data = dates.map((d) => portfolio[d]);
  
  // Le portefeuille a sa propre couleur distincte
  const portfolioColor = 'rgb(34, 197, 94)'; // Un vert vif

  return {
    labels: dates,
    datasets: [
      {
        label: "Valeur du portefeuille",
        data,
        fill: true,
        backgroundColor: `rgba(34, 197, 94, 0.3)`, // ⭐️ Updated color
        borderColor: portfolioColor, // ⭐️ Updated color
        tension: 0.2,
        pointRadius: 0, 
      },
    ],
  };
}

// --- Composant Principal ---

function Charts({ assetPrices, portfolio }) {
  const [dataReady, setDataReady] = useState(false);
  
  const dataPointCount = assetPrices ? Object.keys(assetPrices).length : 0;

  // 1. Memoization pour la transformation des données
  const assetData = useMemo(
    () => buildAssetChartData(assetPrices),
    [assetPrices]
  );
  
  const portfolioData = useMemo(
    () => buildPortfolioChartData(portfolio),
    [portfolio]
  );
  
  // 2. Buffer de rendu (délai de 50ms) pour éviter le blocage du thread
  useEffect(() => {
    if (assetPrices || portfolio) {
      setDataReady(false); 
      const timer = setTimeout(() => {
        setDataReady(true);
      }, 50); 
      
      return () => clearTimeout(timer); 
    }
    setDataReady(false); 
  }, [assetPrices, portfolio]);


  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'top',
        },
        tooltip: {
            mode: 'index',
            intersect: false,
        }
    },
    scales: {
        x: {
            type: 'category',
            title: {
                display: true,
                text: 'Date'
            }
        },
        y: {
            title: {
                display: true,
                text: 'Prix / Valeur'
            }
        }
    }
  };

  const chartStyles = { 
    height: '450px', 
    minHeight: '40vh',
    maxHeight: '45vh',
  };


  return (
    <div className="section chart-container space-y-8">
      
      <p className="text-sm text-gray-700">
        Points de données par actif (max) : {dataPointCount}
      </p>

      {/* Afficher les graphiques UNIQUEMENT si dataReady est true */}
      
      {/* ⭐️ CHANGEMENT: Asset chart affiché en premier (près du bouton) */}
      {dataReady && assetData && (
        <div style={chartStyles}>
          <h2>Courbes des actifs sélectionnés</h2>
          <Line data={assetData} options={chartOptions} />
        </div>
      )}

      {/* Portfolio chart affiché en second (vers le bas de la page) */}
      {dataReady && portfolioData && (
        <div style={chartStyles}>
          <h2>Évolution de la valeur du portefeuille</h2>
          <Line data={portfolioData} options={chartOptions} />
        </div>
      )}
      
      {/* Afficher un message de chargement si les données sont là mais le rendu est en attente */}
      {((assetPrices || portfolio) && !dataReady) && (
          <p className="text-blue-500 font-medium mt-4">Préparation des graphiques en cours...</p>
      )}

      {/* Afficher un message si aucune donnée n'est prête */}
      {!assetPrices && !portfolio && (
          <p className="text-gray-500 italic">Sélectionnez des actifs et chargez les données pour visualiser les courbes.</p>
      )}

    </div>
  );
}

export default Charts;