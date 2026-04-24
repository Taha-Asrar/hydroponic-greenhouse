import React, { useState, useEffect } from "react";
import { io } from "socket.io-client";
import client from "../api/client";
import SensorCard from "../components/SensorCard";
import ActuatorControl from "../components/ActuatorControl";
import "./DashboardPage.css";

export default function DashboardPage() {
  const [capteurs, setCapteurs] = useState([]);
  const [actionneurs, setActionneurs] = useState([]);
  const [hwStatus, setHwStatus] = useState({ connected: false, mock_mode: false });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
    
    const socketUrl = import.meta.env.VITE_API_URL ? import.meta.env.VITE_API_URL.replace('/api', '') : 'http://localhost:5000';
    const socket = io(socketUrl);

    socket.on('connect', () => {
      console.log('Connecté au serveur WebSocket');
    });

    socket.on('actuators_update', (data) => {
      console.log('Mise à jour des actionneurs via Socket.IO:', data);
      setActionneurs(prev => prev.map(a => {
        let updated = { ...a };
        if (data[a.type] !== undefined) {
          updated.actif = data[a.type];
        }
        if (data[`${a.type}_mode`] !== undefined) {
          updated.mode_automatique = data[`${a.type}_mode`] === 'auto';
        }
        return updated;
      }));
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [resCapteurs, resActionneurs, resStatus] = await Promise.all([
        client.get("/capteurs"),
        client.get("/actionneurs"),
        client.get("/actionneurs/status")
      ]);
      setCapteurs(resCapteurs.data || []);
      setActionneurs(resActionneurs.data || []);
      setHwStatus(resStatus.data || { connected: false, mock_mode: false });
      setError(null);
    } catch (err) {
      console.error("Error fetching dashboard data:", err);
      setError("Impossible de charger les données du dashboard.");
    } finally {
      setLoading(false);
    }
  };

  const handleToggleActuator = async (id, newStatus) => {
    try {
      // Optimistic update
      setActionneurs(prev => prev.map(a => a.id_actionneur === id ? { ...a, actif: newStatus, mode_automatique: false } : a));
      await client.post(`/actionneurs/${id}/toggle`, { actif: newStatus });
    } catch (err) {
      console.error("Failed to toggle actuator:", err);
      fetchDashboardData();
    }
  };

  const handleResetAuto = async (id) => {
    try {
      setActionneurs(prev => prev.map(a => a.id_actionneur === id ? { ...a, mode_automatique: true } : a));
      await client.post(`/actionneurs/${id}/auto`);
    } catch (err) {
      console.error("Failed to reset auto mode:", err);
      fetchDashboardData();
    }
  };

  if (loading) return <div className="dashboard-loading"><div className="spinner"></div></div>;

  return (
    <div className="dashboard-page">
      <div className="page-header">
        <div className="header-content">
          <h1 className="page-title">Dashboard</h1>
          <p className="page-subtitle">Vue d'ensemble de la serre hydroponique en temps réel</p>
        </div>
        <div className={`hardware-status ${hwStatus.connected ? 'status-connected' : 'status-disconnected'}`}>
          <span className="status-dot"></span>
          {hwStatus.connected ? 'Arduino Connecté' : 'Arduino Déconnecté'}
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="dashboard-grid">
        <section className="dashboard-section">
          <h2 className="section-title">Capteurs</h2>
          <div className="sensors-grid">
            {capteurs.map(capteur => (
              <SensorCard 
                key={capteur.id_capteur}
                name={capteur.nom}
                type={capteur.type_capteur}
                value={capteur.dernier_releve}
                unit={capteur.unite}
                status={capteur.actif ? "normal" : "warning"}
              />
            ))}
            {capteurs.length === 0 && <p className="empty-state">Aucun capteur détecté.</p>}
          </div>
        </section>

        <section className="dashboard-section">
          <h2 className="section-title">Actionneurs</h2>
          <div className="actuators-grid">
            {actionneurs.map(act => (
              <div key={act.id_actionneur} className="actuator-control-wrapper">
                <ActuatorControl 
                  actuator={act}
                  onToggle={handleToggleActuator}
                />
                {!act.mode_automatique && (
                  <button 
                    className="reset-auto-btn" 
                    onClick={() => handleResetAuto(act.id_actionneur)}
                  >
                    Repasser en Auto
                  </button>
                )}
              </div>
            ))}
            {actionneurs.length === 0 && <p className="empty-state">Aucun actionneur détecté.</p>}
          </div>
        </section>
      </div>
    </div>
  );
}

