// frontend/src/components/WeightAllocator.jsx
import React from "react";

//Allows users to specify the percentage allocation for each selected asset.

function WeightAllocator({ selected, weights, setWeights }) {
  // ide component if no asset is selected
  if (selected.length === 0) return null;

  function handleWeightChange(asset, value) {
    const numValue = parseFloat(value) || 0;
    setWeights({ ...weights, [asset]: numValue });
  }

  //  Calculate total weight allocation
  const totalWeight = selected.reduce((sum, asset) => sum + (weights[asset] || 0), 0); // reduce() iterates over sleected assets and sums their weights
  const isValid = Math.abs(totalWeight - 1.0) < 0.01;

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">
        3. Allocate Weights
      </h2>
      <p className="text-sm text-gray-600 mb-4">
        Assign percentage allocation to each asset (must sum to 100%)
      </p>

      <div className="space-y-3">
        {selected.map((asset) => (
          <div key={asset} className="flex items-center gap-4">
            <label className="w-24 font-medium text-gray-700">
              {asset}
            </label>
            <input
              type="number"
              step="0.01"
              min="0"
              max="1"
              value={weights[asset] || 0}
              onChange={(e) => handleWeightChange(asset, e.target.value)}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg 
                       focus:ring-2 focus:ring-primary-500 focus:border-transparent 
                       outline-none"
            />
            <span className="w-16 text-right text-gray-600">
              {((weights[asset] || 0) * 100).toFixed(0)}%
            </span>
          </div>
        ))}
      </div>

      {/* Validation Indicator */}
      <div className={`mt-4 p-3 rounded-lg ${
        isValid ? 'bg-green-50 border border-green-200' : 'bg-orange-50 border border-orange-200'
      }`}>
        <p className={`text-sm font-medium ${
          isValid ? 'text-green-700' : 'text-orange-700'
        }`}>
          Total: {(totalWeight * 100).toFixed(1)}% 
          {isValid ? ' ✓' : ` (must be 100%)`}
        </p>
      </div>
    </div>
  );
}

export default WeightAllocator;