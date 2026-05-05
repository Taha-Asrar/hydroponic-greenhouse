import { useState, useEffect } from "react";
import { MdNotifications, MdCheck, MdWarning, MdError, MdInfo } from "react-icons/md";
import client from "../api/client";
import "./shared.css";

const SEVERITE_MAP = {
  info:     { icon: <MdInfo />,    badge: "badge-blue",   label: "Info" },
  warning:  { icon: <MdWarning />, badge: "badge-yellow", label: "Avertissement" },
  critique: { icon: <MdError />,   badge: "badge-red",    label: "Critique" },
};

export default function AlertesPage() {
  const [alertes, setAlertes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterSeverite, setFilterSeverite] = useState("");
  const [filterAcquittee, setFilterAcquittee] = useState("");

  useEffect(() => { fetchAlertes(); }, [filterSeverite, filterAcquittee]);

  const fetchAlertes = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (filterSeverite) params.append("severite", filterSeverite);
      if (filterAcquittee) params.append("acquittee", filterAcquittee);
      const res = await client.get(`/alertes?${params.toString()}`);
      setAlertes(res.data || []);
    } catch { setError("Impossible de charger les alertes."); }
    finally { setLoading(false); }
  };

  const acquitter = async (id) => {
    try {
      await client.patch(`/alertes/${id}/acquitter`);
      fetchAlertes();
    } catch { setError("Erreur lors de l'acquittement."); }
  };

  const formatDate = (d) => d ? new Date(d).toLocaleString("fr-FR", {
    day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit",
  }) : "—";

  // Stats
  const nonAcquittees = alertes.filter((a) => !a.acquittee).length;
  const critiques = alertes.filter((a) => a.severite === "critique" && !a.acquittee).length;

  if (loading) return <div className="page-loading"><div className="spinner" /><span>Chargement...</span></div>;

  return (
    <div className="crud-page">
      <div className="page-header">
        <h1 className="page-title">Alertes</h1>
        <p className="page-subtitle">Notifications et derives des parametres du systeme</p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="stats-row">
        <div className="stat-card">
          <div className="stat-label">Non acquittees</div>
          <div className="stat-value" style={{ color: "#fb923c" }}>{nonAcquittees}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Critiques actives</div>
          <div className="stat-value" style={{ color: "#ef4444" }}>{critiques}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total</div>
          <div className="stat-value">{alertes.length}</div>
        </div>
      </div>

      <div className="page-toolbar">
        <div className="toolbar-left">
          <select className="filter-select" value={filterSeverite} onChange={(e) => setFilterSeverite(e.target.value)}>
            <option value="">Toutes les severites</option>
            <option value="info">Info</option>
            <option value="warning">Avertissement</option>
            <option value="critique">Critique</option>
          </select>
          <select className="filter-select" value={filterAcquittee} onChange={(e) => setFilterAcquittee(e.target.value)}>
            <option value="">Toutes</option>
            <option value="false">Non acquittees</option>
            <option value="true">Acquittees</option>
          </select>
        </div>
      </div>

      {alertes.length > 0 ? (
        <div className="data-table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Severite</th>
                <th>Message</th>
                <th>Date</th>
                <th>Statut</th>
                <th style={{ textAlign: "right" }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {alertes.map((a) => {
                const sev = SEVERITE_MAP[a.severite] || SEVERITE_MAP.info;
                return (
                  <tr key={a.id_alerte} style={{ opacity: a.acquittee ? 0.5 : 1 }}>
                    <td><span className={`badge ${sev.badge}`}>{sev.icon} {sev.label}</span></td>
                    <td>{a.message}</td>
                    <td style={{ whiteSpace: "nowrap" }}>{formatDate(a.horodatage)}</td>
                    <td>{a.acquittee ? <span className="badge badge-gray">Acquittee</span> : <span className="badge badge-orange">Active</span>}</td>
                    <td>
                      <div className="td-actions">
                        {!a.acquittee && (
                          <button className="btn btn-success btn-sm" onClick={() => acquitter(a.id_alerte)}><MdCheck /> Acquitter</button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="empty-state">
          <div className="empty-icon">🔔</div>
          <h3>Aucune alerte</h3>
          <p>Le systeme fonctionne normalement. Les alertes apparaitront ici en cas de derive des parametres.</p>
        </div>
      )}
    </div>
  );
}
