// Choix de stratégie (DCA ou buy and hold) + période d’investissement.

// Chemin d'accès:
// frontend/src/components/StrategyForm.jsx

import React from "react";

function StrategyForm({ strategy, setStrategy }) {
  function handleChange(e) {
    const { name, value } = e.target;
    setStrategy({
      ...strategy,
      [name]: value,
    });
  }

  return (
    <div className="section">
      <h2>Stratégie d'investissement</h2>
      <div>
        <label>Type de stratégie :</label>
        <select
          name="type"
          value={strategy.type}
          onChange={handleChange}
        >
          <option value="buy_and_hold">Buy and Hold</option>
          <option value="dca">DCA (Dollar-Cost Averaging)</option>
        </select>
      </div>
      <div>
        <label>Début de la stratégie :</label>
        <input
          type="date"
          name="stratStart"
          value={strategy.stratStart}
          onChange={handleChange}
        />
      </div>
      <div>
        <label>Fin de la stratégie :</label>
        <input
          type="date"
          name="stratEnd"
          value={strategy.stratEnd}
          onChange={handleChange}
        />
      </div>
    </div>
  );
}

export default StrategyForm;
