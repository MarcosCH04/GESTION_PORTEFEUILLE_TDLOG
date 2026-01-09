// Période de backtest des actifs (pour les courbes et les métriques).

// Chemin d'accès: 
// frontend/src/components/PeriodSelector.jsx

import React from "react";

function PeriodSelector({ period, setPeriod }) {
  function handleChange(e) {
    const { name, value } = e.target;
    setPeriod({
      ...period,
      [name]: value,
    });
  }

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">
        2. Analysis Period
      </h2>
      <p className="text-sm text-gray-600 mb-4">
        Select the historical date range for asset analysis
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Start Date
          </label>
          <input
            type="date"
            name="start"
            value={period.start}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg 
                     focus:ring-2 focus:ring-primary-500 focus:border-transparent 
                     outline-none"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            End Date
          </label>
          <input
            type="date"
            name="end"
            value={period.end}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg 
                     focus:ring-2 focus:ring-primary-500 focus:border-transparent 
                     outline-none"
          />
        </div>
      </div>
    </div>
  );
}

export default PeriodSelector;