// frontend/src/components/AssetSelector.jsx

import React from "react";

//Allows users to select multiple assets for portfolio analysis.

function AssetSelector({ assets, selected, setSelected }) {
  // Toggle asset selection
  // If asset is already selected, it is removeed otherwise it is added
  function toggle(asset) {
    if (selected.includes(asset)) {
      setSelected(selected.filter((s) => s !== asset));
    } else {
      setSelected([...selected, asset]);
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">
        1. Select Assets
      </h2>
      <p className="text-sm text-gray-600 mb-4">
        Choose the assets you want to include in your portfolio
      </p>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {assets.map((asset) => (
          <button
            key={asset}
            onClick={() => toggle(asset)}
            className={`
              px-4 py-3 rounded-lg font-medium transition-all duration-200
              ${selected.includes(asset)
                ? 'bg-primary-500 text-white shadow-md'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }
            `}
          >
            {asset}
          </button>
        ))}
      </div>

      {selected.length > 0 && (
        <div className="mt-4 p-3 bg-blue-50 rounded-lg">
          <p className="text-sm text-blue-700">
            <strong>{selected.length}</strong> asset{selected.length > 1 ? 's' : ''} selected: {selected.join(', ')}
          </p>
        </div>
      )}
    </div>
  );
}

export default AssetSelector;