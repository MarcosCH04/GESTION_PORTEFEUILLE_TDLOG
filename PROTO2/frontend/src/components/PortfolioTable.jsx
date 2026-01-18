// frontend/src/components/PortfolioTable.jsx
import React from "react";

/**
 * Displays performance metrics for each selected asset in a clean table format.
 */
function PortfolioTable({ selectedAssets, metrics }) {
  // Hide table if no data available
  if (!metrics || selectedAssets.length === 0) {
    return null;
  }

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">
        4. Performance Metrics
      </h2>
      <p className="text-sm text-gray-600 mb-4">
        Detailed performance analysis for each selected asset
      </p>

      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          {/* Table Header */}
          <thead>
            <tr className="bg-gray-50 border-b-2 border-gray-200">
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Asset
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">
                CAGR
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Annualized Return
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Volatility
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Best Year
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Worst Year
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Max Drawdown
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Sharpe Ratio
              </th>
            </tr>
          </thead>

          {/* Table Body */}
          <tbody className="divide-y divide-gray-200">
            {selectedAssets.map((asset, index) => {
              const m = metrics[asset];
              if (!m) return null;

              return (
                <tr 
                  key={asset} 
                  className={`
                    ${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
                    hover:bg-gray-100 transition-colors
                  `}
                >
                  {/* Asset Name */}
                  <td className="px-4 py-3 text-left font-semibold text-gray-900">
                    {asset}
                  </td>

                  {/* CAGR */}
                  <td className="px-4 py-3 text-right font-medium text-gray-700">
                    {(m.cagr * 100).toFixed(2)}%
                  </td>

                  {/* Annualized Return */}
                  <td className="px-4 py-3 text-right font-medium text-gray-700">
                    {(m.annualized_return * 100).toFixed(2)}%
                  </td>

                  {/* Volatility */}
                  <td className="px-4 py-3 text-right text-gray-700">
                    {(m.vol * 100).toFixed(2)}%
                  </td>

                  {/* Best Year */}
                  <td className="px-4 py-3 text-right font-medium text-gray-700">
                    {(m.best_year * 100).toFixed(2)}%
                  </td>

                  {/* Worst Year */}
                  <td className="px-4 py-3 text-right font-medium text-gray-700">
                    {(m.worst_year * 100).toFixed(2)}%
                  </td>

                  {/* Max Drawdown */}
                  <td className="px-4 py-3 text-right font-medium text-gray-700">
                    {(m.max_drawdown * 100).toFixed(2)}%
                  </td>

                  {/* Sharpe Ratio */}
                  <td className="px-4 py-3 text-right font-medium text-gray-700">
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
