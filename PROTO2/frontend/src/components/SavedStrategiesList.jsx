import React, { useEffect, useState } from "react";
import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

function SavedStrategiesList({ savedStrats, onRefresh, onLoadStrategy }) {
  
  const handleDelete = async (id) => {
    if (!window.confirm("Supprimer cette stratégie ?")) return;
    try {
      await axios.delete(`${API_BASE_URL}/strategies/${id}`);
      onRefresh(); // Calls refreshStrategies in App.jsx
    } catch (err) {
      alert("Erreur lors de la suppression");
    }
  };

  return (
    <div className="section saved-strategies">
      <h2>Mes Stratégies</h2>
      {savedStrats.length === 0 ? (
        <p>Lancez un backtest pour voir apparaître votre dernière stratégie.</p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {savedStrats.map((strat) => (
            <li key={strat.id} style={{ 
                borderBottom: "1px solid #ccc", 
                padding: "10px 0",
                backgroundColor: !strat.is_saved ? "#f9f9f9" : "transparent" 
            }}>
              <strong>{strat.name}</strong> 
              {!strat.is_saved && <span style={{color: 'green', marginLeft: '10px'}}>(Prête à être sauvegardée)</span>}
              
              <div style={{ marginTop: "5px" }}>
                <button onClick={() => onLoadStrategy(strat.parameters)}>Charger</button>
                
                {strat.is_saved && (
                  <button 
                    onClick={() => handleDelete(strat.id)} 
                    style={{ marginLeft: "10px", color: "red" }}
                  >
                    Supprimer
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default SavedStrategiesList;