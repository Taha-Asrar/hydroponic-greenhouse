import React from "react";
import "./SensorCard.css";

export default function SensorCard({ name, value, unit, type, status = "normal" }) {
  const getTypeStyles = () => {
    switch (type) {
      case "temp_eau":
        return { color: "var(--accent-blue)", icon: "🌡️" };
      case "temp_air":
        return { color: "var(--accent-orange)", icon: "🌡️" };
      case "humidite":
        return { color: "var(--accent-blue)", icon: "💧" };
      case "niveau_eau":
        return { color: "var(--accent-blue)", icon: "🌊" };
      case "luminosite":
        return { color: "var(--accent-yellow)", icon: "☀️" };
      default:
        return { color: "var(--text-secondary)", icon: "📊" };
    }
  };

  const { color, icon } = getTypeStyles();

  // Format display value
  const displayValue = value !== null && value !== undefined ? 
    (typeof value === 'number' ? value.toFixed(1) : value) : "--";

  return (
    <div className={`sensor-card status-${status}`}>
      <div className="sensor-card-header">
        <span className="sensor-icon" style={{ color }}>{icon}</span>
        <h3 className="sensor-name">{name}</h3>
      </div>
      <div className="sensor-card-body">
        <div className="sensor-value-container" style={{ '--glow-color': color }}>
          <span className="sensor-value">{displayValue}</span>
          <span className="sensor-unit">{unit}</span>
        </div>
      </div>
      {status !== "normal" && (
        <div className="sensor-alert">
          ⚠ Alerte détectée
        </div>
      )}
    </div>
  );
}
