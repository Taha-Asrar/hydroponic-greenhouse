import { useState, useEffect } from "react";
import { MdSettings, MdUsb, MdStorage, MdWifi, MdInfo } from "react-icons/md";
import { useAuth } from "../context/AuthContext";
import client from "../api/client";
import "./shared.css";

export default function SettingsPage() {
  const { user } = useAuth();
  const [health, setHealth] = useState(null);
  const [status, setStatus] = useState({ connected: false, mock_mode: false });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [resHealth, resStatus] = await Promise.all([
          client.get("/health"),
          client.get("/actionneurs/status")
        ]);
        setHealth(resHealth.data);
        setStatus(resStatus.data);
      } catch { 
        setHealth({ status: "erreur", service: "N/A", version: "N/A" }); 
      } finally { 
        setLoading(false); 
      }
    };
    fetchData();
  }, []);

  if (loading) return <div className="page-loading"><div className="spinner" /><span>Chargement...</span></div>;

  return (
    <div className="crud-page">
      <div className="page-header">
        <h1 className="page-title">Parametres</h1>
        <p className="page-subtitle">Configuration et informations systeme</p>
      </div>

      {/* System Status */}
      <div className="stats-row">
        <div className="stat-card">
          <div className="stat-label"><MdWifi style={{ verticalAlign: "middle" }} /> API</div>
          <div className="stat-value" style={{ color: health?.status === "ok" ? "#4ade80" : "#ef4444", fontSize: "1.2rem" }}>
            {health?.status === "ok" ? "En ligne" : "Hors ligne"}
          </div>
          <div className="stat-sub">{health?.service}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label"><MdInfo style={{ verticalAlign: "middle" }} /> Version</div>
          <div className="stat-value" style={{ fontSize: "1.2rem" }}>{health?.version || "—"}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label"><MdUsb style={{ verticalAlign: "middle" }} /> Port Serie</div>
          <div className="stat-value" style={{ 
            fontSize: "1.2rem", 
            color: status.connected ? "#4ade80" : (status.mock_mode ? "#fb923c" : "#ef4444") 
          }}>
            {status.connected ? "Connecté" : (status.mock_mode ? "Simulation" : "Déconnecté")}
          </div>
          <div className="stat-sub">Port: COM3</div>
        </div>
        <div className="stat-card">
          <div className="stat-label"><MdStorage style={{ verticalAlign: "middle" }} /> Base de donnees</div>
          <div className="stat-value" style={{ fontSize: "1.2rem", color: "#3b82f6" }}>PostgreSQL</div>
          <div className="stat-sub">serre_hydroponique</div>
        </div>
      </div>

      {/* User Info Section */}
      <div className="chart-container" style={{ marginBottom: 24 }}>
        <div className="chart-header">
          <h3 className="chart-title"><MdSettings style={{ verticalAlign: "middle", marginRight: 8 }} />Profil utilisateur</h3>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          <div className="form-group">
            <label>Prenom</label>
            <input className="form-input" readOnly value={user?.prenom || "—"} />
          </div>
          <div className="form-group">
            <label>Nom</label>
            <input className="form-input" readOnly value={user?.nom || "—"} />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input className="form-input" readOnly value={user?.email || "—"} />
          </div>
          <div className="form-group">
            <label>Role</label>
            <input className="form-input" readOnly value={user?.role || "—"} style={{ textTransform: "capitalize" }} />
          </div>
        </div>
      </div>

      {/* Architecture Info */}
      <div className="chart-container">
        <div className="chart-header">
          <h3 className="chart-title"><MdInfo style={{ verticalAlign: "middle", marginRight: 8 }} />Architecture du systeme</h3>
        </div>
        <div style={{ color: "var(--text-muted)", lineHeight: 1.8, fontSize: "0.9rem" }}>
          <p><strong>Backend :</strong> Flask + SQLAlchemy + Flask-SocketIO + APScheduler</p>
          <p><strong>Frontend :</strong> React 19 + Vite + Recharts + Socket.IO Client</p>
          <p><strong>Base de donnees :</strong> PostgreSQL 16</p>
          <p><strong>Communication :</strong> Port serie USB (Arduino UNO) via PySerial</p>
          <p><strong>Logique metier :</strong> Systeme Ebb & Flow (Table a Maree) — evaluation toutes les 10 secondes</p>
          <p><strong>Temps reel :</strong> WebSocket via Socket.IO pour les mises a jour des actionneurs et lectures de capteurs</p>
        </div>
      </div>
    </div>
  );
}
