// frontend/src/components/SavedStrategiesList.jsx
import React, { useEffect, useState } from "react";
import axios from "axios";

//API base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

function SavedStrategiesList({ savedStrats = [], onRefresh, onLoadStrategy }) {
  // Loading state while fetching strategies
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(false);
  }, [savedStrats]);

  // Handle strategy deletion with confirmation
  const handleDelete = async (id, name) => {
    if (!window.confirm(`Delete strategy "${name}"?`)) return;

    try {
      // Send DELETE request to backend to remove strategy
      await axios.delete(`${API_BASE_URL}/strategies/${id}`);
      onRefresh();
    } catch (err) {
      // Show error if deletion fails 
      alert("Failed to delete strategy");
    }
  };

  // Show loading state while fetching strategies
  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-6">
        <p className="text-gray-500">Loading strategies...</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">
        5. Saved Strategies
      </h2>

      {savedStrats.length === 0 ? (
        <p className="text-gray-500">No saved strategies yet</p>
      ) : (
        <div className="space-y-3">
          {savedStrats.map((strat) => (
            <div key={strat.id} className="border p-4 rounded-lg">
              <h3 className="font-semibold">{strat.name}</h3>

              <div className="flex gap-2 mt-2">
                <button
                  onClick={() => onLoadStrategy(strat.parameters)}
                  className="px-3 py-1 bg-blue-500 text-white rounded"
                >
                  Load
                </button>

                <button
                  onClick={() => handleDelete(strat.id, strat.name)}
                  className="px-3 py-1 bg-red-500 text-white rounded"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default SavedStrategiesList;
