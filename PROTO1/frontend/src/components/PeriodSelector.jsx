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
    <div className="section">
      <h2>Période d'analyse des actifs</h2>
      <div>
        <label>Début :</label>
        <input
          type="date"
          name="start"
          value={period.start}
          onChange={handleChange}
        />
      </div>
      <div>
        <label>Fin :</label>
        <input
          type="date"
          name="end"
          value={period.end}
          onChange={handleChange}
        />
      </div>
    </div>
  );
}

export default PeriodSelector;
