import React from "react";
import "./ActuatorControl.css";

export default function ActuatorControl({ actuator, onToggle }) {
  const { id_actionneur, nom, type, actif } = actuator;

  const handleToggle = () => {
    onToggle(id_actionneur, !actif);
  };

  const getIcon = () => {
    switch (type) {
      case "pompe_alimentation":
        return "🌊";
      case "pompe_evacuation":
        return "🔄";
      case "eclairage":
        return "💡";
      case "ventilateur":
        return "💨";
      default:
        return "⚙️";
    }
  };

  return (
    <div className={`actuator-card ${actif ? "is-active" : ""}`}>
      <div className="actuator-icon">{getIcon()}</div>
      <div className="actuator-info">
        <h3>{nom}</h3>
        <span className="actuator-status">{actif ? "EN MARCHE" : "À L'ARRÊT"}</span>
      </div>
      <button 
        className={`actuator-toggle ${actif ? "active" : ""}`} 
        onClick={handleToggle}
        aria-label={`Toggle ${nom}`}
      >
        <div className="toggle-thumb" />
      </button>
    </div>
  );
}
