import { useState, useEffect, useRef } from "react";
import { io } from "socket.io-client";
import {
  XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Area, AreaChart,
} from "recharts";
import { MdSensors, MdRefresh } from "react-icons/md";
import client from "../api/client";
import "./shared.css";

const SENSOR_CONFIG = {
  temp_eau:   { color: "#3b82f6", unit: "°C",  icon: "🌡" },
  temp_air:   { color: "#fb923c", unit: "°C",  icon: "🌡" },
  humidite:   { color: "#22d3ee", unit: "%",   icon: "💧" },
  luminosite: { color: "#facc15", unit: "%",   icon: "☀" },
  niveau_eau: { color: "#4ade80", unit: "%",   icon: "🌊" },
};

export default function CapteursPage() {
  const [capteurs, setCapteurs] = useState([]);
  const [selectedCapteur, setSelectedCapteur] = useState(null);
  const [lectures, setLectures] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const selectedRef = useRef(null);

  useEffect(() => {
    fetchCapteurs();

    const socketUrl = import.meta.env.VITE_API_URL
      ? import.meta.env.VITE_API_URL.replace("/api", "")
      : "http://localhost:5000";
    const socket = io(socketUrl);

    socket.on("nouvelles_lectures", (data) => {
      // Update capteurs values in real-time
      setCapteurs(prev => prev.map(c => {
        if (data[c.type_capteur] !== undefined) {
          return { ...c, dernier_releve: data[c.type_capteur] };
        }
        return c;
      }));

      // Add new point to chart if selected sensor has new data
      if (selectedRef.current && data[selectedRef.current.type_capteur] !== undefined) {
        const newPoint = {
          valeur: data[selectedRef.current.type_capteur],
          time: new Date().toLocaleTimeString("fr-FR", {
            hour: "2-digit", minute: "2-digit", second: "2-digit",
          }),
        };
        setLectures(prev => [...prev.slice(-49), newPoint]);
      }
    });

    return () => socket.disconnect();
  }, []);

  useEffect(() => {
    selectedRef.current = selectedCapteur;
    if (selectedCapteur) fetchLectures(selectedCapteur.id_capteur);
  }, [selectedCapteur]);

  const fetchCapteurs = async () => {
    try {
      setLoading(true);
      const res = await client.get("/capteurs");
      // Filter out inactive sensors (like EC)
      const data = (res.data || []).filter(c => c.actif !== false);
      setCapteurs(data);
      if (data.length > 0 && !selectedCapteur) setSelectedCapteur(data[0]);
    } catch (err) {
      setError("Impossible de charger les capteurs.");
    } finally {
      setLoading(false);
    }
  };

  const fetchLectures = async (idCapteur) => {
    try {
      const res = await client.get(`/lectures?id_capteur=${idCapteur}&limit=50`);
      const raw = (res.data || []).reverse();
      setLectures(
        raw.map((l) => ({
          ...l,
          time: new Date(l.horodatage).toLocaleTimeString("fr-FR", {
            hour: "2-digit", minute: "2-digit",
          }),
        }))
      );
    } catch {
      setLectures([]);
    }
  };

  if (loading) {
    return (
      <div className="page-loading">
        <div className="spinner" />
        <span>Chargement des capteurs...</span>
      </div>
    );
  }

  const cfg = selectedCapteur ? SENSOR_CONFIG[selectedCapteur.type_capteur] || {} : {};

  return (
    <div className="crud-page">
      <div className="page-header">
        <h1 className="page-title">Capteurs</h1>
        <p className="page-subtitle">Surveillance en temps réel des capteurs de la serre</p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {/* Stats row */}
      <div className="stats-row">
        {capteurs.map((c) => {
          const sc = SENSOR_CONFIG[c.type_capteur] || {};
          return (
            <div
              key={c.id_capteur}
              className={`stat-card ${selectedCapteur?.id_capteur === c.id_capteur ? "stat-card--selected" : ""}`}
              onClick={() => setSelectedCapteur(c)}
              style={{ cursor: "pointer", borderColor: selectedCapteur?.id_capteur === c.id_capteur ? sc.color : undefined }}
            >
              <div className="stat-label">{sc.icon} {c.nom}</div>
              <div className="stat-value" style={{ color: sc.color }}>
                {c.dernier_releve !== null && c.dernier_releve !== undefined
                  ? Number(c.dernier_releve).toFixed(1)
                  : "--"}
              </div>
              <div className="stat-sub">{sc.unit}</div>
            </div>
          );
        })}
      </div>

      {/* Chart */}
      {selectedCapteur && (
        <div className="chart-container">
          <div className="chart-header">
            <h3 className="chart-title">
              <MdSensors style={{ verticalAlign: "middle", marginRight: 8 }} />
              {selectedCapteur.nom} — Historique
            </h3>
            <button className="btn btn-secondary btn-sm" onClick={() => fetchLectures(selectedCapteur.id_capteur)}>
              <MdRefresh /> Rafraîchir
            </button>
          </div>

          {lectures.length > 0 ? (
            <ResponsiveContainer width="100%" height={320}>
              <AreaChart data={lectures}>
                <defs>
                  <linearGradient id="colorVal" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={cfg.color || "#4ade80"} stopOpacity={0.3} />
                    <stop offset="95%" stopColor={cfg.color || "#4ade80"} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="time" stroke="rgba(255,255,255,0.3)" fontSize={12} />
                <YAxis stroke="rgba(255,255,255,0.3)" fontSize={12} />
                <Tooltip
                  contentStyle={{ background: "#1a2736", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 12 }}
                  labelStyle={{ color: "rgba(255,255,255,0.6)" }}
                  itemStyle={{ color: cfg.color }}
                />
                <Area
                  type="monotone" dataKey="valeur"
                  stroke={cfg.color || "#4ade80"} strokeWidth={2}
                  fill="url(#colorVal)"
                  dot={false} activeDot={{ r: 5 }}
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty-state">
              <div className="empty-icon">📊</div>
              <h3>Aucune lecture enregistrée</h3>
              <p>Les données apparaîtront ici lorsque le système commencera à enregistrer les lectures.</p>
            </div>
          )}
        </div>
      )}

      {capteurs.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">🔌</div>
          <h3>Aucun capteur configuré</h3>
          <p>Exécutez le script de seed pour ajouter des capteurs.</p>
        </div>
      )}
    </div>
  );
}
