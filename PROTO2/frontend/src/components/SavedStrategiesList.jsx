import React, { useEffect, useState } from "react";
import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

function SavedStrategiesList({ onLoadStrategy }) {
  const [savedStrats, setSavedStrats] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchSaved = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/strategies`);
      setSavedStrats(res.data);
    } catch (err) {
      console.error("Failed to fetch strategies", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSaved();
  }, []);

  const handleDelete = async (id) => {
    if (!window.confirm("Supprimer cette stratégie ?")) return;
    try {
      await axios.delete(`${API_BASE_URL}/strategies/${id}`);
      setSavedStrats(savedStrats.filter((s) => s.id !== id));
    } catch (err) {
      alert("Erreur lors de la suppression");
    }
  };

  if (loading) return <p>Chargement des stratégies...</p>;

  return (
    <div className="section saved-strategies">
      <h2>Mes Stratégies Sauvegardées</h2>
      {savedStrats.length === 0 ? (
        <p>Aucune stratégie enregistrée (limite: 5).</p>
      ) : (
          <ul style={{ listStyle: "none", padding: 0 }}>
            {savedStrats.map((strat) => (
              <li key={strat.id} style={{ borderBottom: "1px solid #ccc", padding: "10px 0" }}>
                <strong>{strat.name}</strong> - {new Date(strat.created_at).toLocaleDateString()}
                <div style={{ marginTop: "5px" }}>
                  <button onClick={() => onLoadStrategy(strat.parameters)}>Charger</button>
                  <button 
                    onClick={() => handleDelete(strat.id)} 
                    style={{ marginLeft: "10px", color: "red" }}
                  >
                    Supprimer
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
    </div>
  );
}

export default SavedStrategiesList;