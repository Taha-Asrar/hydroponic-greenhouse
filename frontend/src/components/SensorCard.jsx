import React from "react";
import "./SensorCard.css";

export default function SensorCard({ name, value, unit, type, status = "normal" }) {
  // Select icon/color based on sensor type
  const getTypeStyles = () => {
    switch (type) {
      case "temp_eau":
      case "temp_air":
        return { color: "var(--accent-orange)", icon: "🌡️" };
      case "humidite":
      case "niveau_eau":
        return { color: "var(--accent-blue)", icon: "💧" };
      case "EC":
        return { color: "var(--accent-purple)", icon: "⚡" };
      case "luminosite":
        return { color: "var(--accent-yellow)", icon: "☀️" };
      default:
        return { color: "var(--text-secondary)", icon: "📊" };
    }
  };

  const { color, icon } = getTypeStyles();

  return (
    <div className={`sensor-card status-${status}`}>
      <div className="sensor-card-header">
        <span className="sensor-icon" style={{ color }}>{icon}</span>
        <h3 className="sensor-name">{name}</h3>
      </div>
      <div className="sensor-card-body">
        <div className="sensor-value-container" style={{ '--glow-color': color }}>
          <span className="sensor-value">{value !== null ? value : "--"}</span>
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
