// Choix de stratégie (DCA ou buy and hold) + période d’investissement.

// Chemin d'accès:
// frontend/src/components/StrategyForm.jsx

// frontend/src/components/StrategyForm.jsx
import React from "react";

function StrategyForm({ strategy, setStrategy, amount, setAmount }) {
  function handleChange(e) {
    const { name, value } = e.target;
    setStrategy({ ...strategy, [name]: value });
  }

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">
        4. Investment Strategy
      </h2>
      <p className="text-sm text-gray-600 mb-6">
        Configure your investment amount and strategy parameters
      </p>
      
      {/* Montant */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Total Investment Amount ($)
        </label>
        <input
          type="number"
          value={amount}
          onChange={(e) => setAmount(Number(e.target.value))}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg 
                   focus:ring-2 focus:ring-primary-500 focus:border-transparent 
                   outline-none"
          placeholder="10000"
        />
      </div>

      {/* Type de stratégie */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Strategy Type
        </label>
        <select
          name="type"
          value={strategy.type}
          onChange={handleChange}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg 
                   focus:ring-2 focus:ring-primary-500 focus:border-transparent 
                   outline-none bg-white"
        >
          <option value="buy_and_hold">Buy and Hold</option>
          <option value="dca">Dollar-Cost Averaging (DCA)</option>
        </select>
      </div>

      {/* Dates de stratégie */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Strategy Start Date
          </label>
          <input
            type="date"
            name="stratStart"
            value={strategy.stratStart}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg 
                     focus:ring-2 focus:ring-primary-500 focus:border-transparent 
                     outline-none"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Strategy End Date
          </label>
          <input
            type="date"
            name="stratEnd"
            value={strategy.stratEnd}
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

export default StrategyForm;