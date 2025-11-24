// Affiche, pour chaque actif sélectionné, CAGR / Vol / Max Drawdown.

// Chemin d'accès:
// frontend/src/components/PortfolioTable.jsx

import React from "react";

/**
 * metrics est un objet :
 * {
 *   "AAPL": { cagr: ..., vol: ..., max_drawdown: ... },
 *   ...
 * }
 */
function PortfolioTable({ selectedAssets, metrics }) {
  if (!metrics || selectedAssets.length === 0) {
    return null;
  }

  return (
    <div className="section">
      <h2>Métriques par actif</h2>
      <table>
        <thead>
          <tr>
            <th>Actif</th>
            <th>CAGR</th>
            <th>Volatilité</th>
            <th>Max Drawdown</th>
          </tr>
        </thead>
        <tbody>
          {selectedAssets.map((asset) => {
            const m = metrics[asset];
            if (!m) return null;
            return (
              <tr key={asset}>
                <td>{asset}</td>
                <td>{(m.cagr * 100).toFixed(2)} %</td>
                <td>{(m.vol * 100).toFixed(2)} %</td>
                <td>{(m.max_drawdown * 100).toFixed(2)} %</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export default PortfolioTable;
