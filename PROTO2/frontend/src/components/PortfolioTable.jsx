// frontend/src/components/PortfolioTable.jsx

import React from "react";
import "./PortfolioTable.css"; // Importer le fichier CSS

/**
 * Displays performance metrics for each selected asset in a clean table format.
 * Metrics include: CAGR, Annualized Return, Volatility, Best Year, Worst Year, Max Drawdown, Sharpe Ratio
 */
function PortfolioTable({ selectedAssets, metrics }) {
  if (!metrics || selectedAssets.length === 0) {
    return null;
  }

  return (
    <div className="portfolio-table-container">
      <h2 className="table-title">Performance Metrics by Asset</h2>
      <div className="table-wrapper">
        <table className="modern-table">
          <thead>
            <tr>
              <th className="asset-column">Asset</th>
              <th>CAGR</th>
              <th>Annualized Return</th>
              <th>Volatility</th>
              <th>Best Year</th>
              <th>Worst Year</th>
              <th>Max Drawdown</th>
              <th>Sharpe Ratio</th>
            </tr>
          </thead>
          <tbody>
            {selectedAssets.map((asset, index) => {
              const m = metrics[asset];
              if (!m) return null;
              return (
                <tr key={asset} className={index % 2 === 0 ? "row-even" : "row-odd"}>
                  <td className="asset-name">{asset}</td>
                  <td className={m.cagr >= 0 ? "positive" : "negative"}>
                    {(m.cagr * 100).toFixed(2)}%
                  </td>
                  <td className={m.annualized_return >= 0 ? "positive" : "negative"}>
                    {(m.annualized_return * 100).toFixed(2)}%
                  </td>
                  <td>{(m.vol * 100).toFixed(2)}%</td>
                  <td className="positive">{(m.best_year * 100).toFixed(2)}%</td>
                  <td className="negative">{(m.worst_year * 100).toFixed(2)}%</td>
                  <td className="negative">{(m.max_drawdown * 100).toFixed(2)}%</td>
                  <td className={m.sharpe_ratio >= 0 ? "positive" : "negative"}>
                    {m.sharpe_ratio.toFixed(2)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default PortfolioTable;
