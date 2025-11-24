
// Chemin d'accès:
// frontend/src/components/AssetSelector.jsx

import React from "react";

function AssetSelector({ assets, selected, setSelected, weights, setWeights }) {
  function toggle(asset) {
    if (selected.includes(asset)) {
      // On retire l'actif
      const newSelected = selected.filter((s) => s !== asset);
      const newWeights = { ...weights };
      delete newWeights[asset];
      setSelected(newSelected);
      setWeights(newWeights);
    } else {
      // On ajoute l'actif
      const newSelected = [...selected, asset];
      const newWeights = { ...weights };
      newWeights[asset] = 1 / newSelected.length;
      setSelected(newSelected);
      setWeights(newWeights);
    }
  }

  function changeWeight(asset, value) {
    const v = Number(value);
    if (Number.isNaN(v)) return;
    setWeights({
      ...weights,
      [asset]: v,
    });
  }

  return (
    <div className="section">
      <h2>Liste des actifs</h2>
      {assets.map((asset) => (
        <div key={asset}>
          <label>
            <input
              type="checkbox"
              checked={selected.includes(asset)}
              onChange={() => toggle(asset)}
            />
            {asset}
          </label>
          {selected.includes(asset) && (
            <>
              {"  "}Poids (entre 0 et 1) :
              <input
                type="number"
                step="0.01"
                value={weights[asset] ?? 0}
                onChange={(e) => changeWeight(asset, e.target.value)}
              />
            </>
          )}
        </div>
      ))}
    </div>
  );
}

export default AssetSelector;
