import React, { useState, useEffect } from "react";
import { io } from "socket.io-client";
import client from "../api/client";
import SensorCard from "../components/SensorCard";
import ActuatorControl from "../components/ActuatorControl";
import "./DashboardPage.css";

export default function DashboardPage() {
  const [capteurs, setCapteurs] = useState([]);
  const [actionneurs, setActionneurs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
    
    // Configurer Socket.IO
    const socketUrl = import.meta.env.VITE_API_URL ? import.meta.env.VITE_API_URL.replace('/api', '') : 'http://localhost:5000';
    const socket = io(socketUrl);

    socket.on('connect', () => {
      console.log('Connecté au serveur WebSocket');
    });

    socket.on('actuators_update', (data) => {
      console.log('Mise à jour des actionneurs via Socket.IO:', data);
      setActionneurs(prev => prev.map(a => {
        if (a.type === 'pompe_alimentation' && data.pompe_alimentation !== undefined) {
          return { ...a, actif: data.pompe_alimentation };
        }
        if (a.type === 'pompe_evacuation' && data.pompe_evacuation !== undefined) {
          return { ...a, actif: data.pompe_evacuation };
        }
        return a;
      }));
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      // We assume endpoints /capteurs and /actionneurs exist
      const [resCapteurs, resActionneurs] = await Promise.all([
        client.get("/capteurs/"),
        client.get("/actionneurs/")
      ]);
      setCapteurs(resCapteurs.data || []);
      setActionneurs(resActionneurs.data || []);
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
      setActionneurs(prev => prev.map(a => a.id_actionneur === id ? { ...a, actif: newStatus } : a));
      
      // Call API
      // await client.post(`/actionneurs/${id}/toggle`, { actif: newStatus });
      // For now, if the endpoint doesn't exist, we just simulate it
    } catch (err) {
      console.error("Failed to toggle actuator:", err);
      // Revert on failure
      fetchDashboardData();
    }
  };

  if (loading) return <div className="dashboard-loading"><div className="spinner"></div></div>;

  return (
    <div className="dashboard-page">
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">Vue d'ensemble de la serre hydroponique en temps réel</p>
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
                value={capteur.dernier_releve || (Math.random() * 10 + 20).toFixed(1)} // Mock value for now
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
              <ActuatorControl 
                key={act.id_actionneur}
                actuator={act}
                onToggle={handleToggleActuator}
              />
            ))}
            {actionneurs.length === 0 && <p className="empty-state">Aucun actionneur détecté.</p>}
          </div>
        </section>
      </div>
    </div>
  );
}

