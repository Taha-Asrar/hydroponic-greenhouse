import { useState, useEffect } from "react";
import { MdAdd, MdClose, MdTrendingUp } from "react-icons/md";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer,
} from "recharts";
import client from "../api/client";
import "./shared.css";

export default function SuiviPage() {
  const [suivis, setSuivis] = useState([]);
  const [cycles, setCycles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [filterCycle, setFilterCycle] = useState("");
  const [form, setForm] = useState({
    id_cycle: "", date_mesure: new Date().toISOString().split("T")[0],
    hauteur_cm: "", poids_g: "", observations: "",
  });

  useEffect(() => { fetchAll(); }, []);

  useEffect(() => { fetchSuivis(); }, [filterCycle]);

  const fetchAll = async () => {
    try {
      setLoading(true);
      const [cRes] = await Promise.all([client.get("/cycles")]);
      setCycles(cRes.data || []);
      await fetchSuivis();
    } catch { setError("Impossible de charger les donnees."); }
    finally { setLoading(false); }
  };

  const fetchSuivis = async () => {
    try {
      const params = filterCycle ? `?id_cycle=${filterCycle}` : "";
      const res = await client.get(`/suivi${params}`);
      setSuivis(res.data || []);
    } catch { /* ignore */ }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        id_cycle: parseInt(form.id_cycle),
        date_mesure: form.date_mesure,
      };
      if (form.hauteur_cm) payload.hauteur_cm = parseFloat(form.hauteur_cm);
      if (form.poids_g) payload.poids_g = parseFloat(form.poids_g);
      if (form.observations) payload.observations = form.observations;

      await client.post("/suivi", payload);
      setShowModal(false);
      fetchSuivis();
    } catch (err) { setError(err.response?.data?.error || "Erreur."); }
  };

  const formatDate = (d) => d ? new Date(d).toLocaleDateString("fr-FR") : "—";

  // Chart data: growth curve
  const chartData = [...suivis]
    .filter((s) => s.hauteur_cm)
    .reverse()
    .map((s) => ({
      date: new Date(s.date_mesure).toLocaleDateString("fr-FR", { day: "2-digit", month: "short" }),
      hauteur: s.hauteur_cm,
      poids: s.poids_g,
    }));

  const cyclesActifs = cycles.filter((c) => c.statut === "en_cours");

  if (loading) return <div className="page-loading"><div className="spinner" /><span>Chargement...</span></div>;

  return (
    <div className="crud-page">
      <div className="page-header">
        <h1 className="page-title">Suivi de Croissance</h1>
        <p className="page-subtitle">Historique des mesures et evolution des plantes</p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="page-toolbar">
        <div className="toolbar-left">
          <select className="filter-select" value={filterCycle} onChange={(e) => setFilterCycle(e.target.value)}>
            <option value="">Tous les cycles</option>
            {cycles.map((c) => <option key={c.id_cycle} value={c.id_cycle}>Cycle #{c.id_cycle} ({c.statut})</option>)}
          </select>
        </div>
        <button className="btn btn-primary" onClick={() => {
          setForm({
            id_cycle: cyclesActifs[0]?.id_cycle || "",
            date_mesure: new Date().toISOString().split("T")[0],
            hauteur_cm: "", poids_g: "", observations: "",
          });
          setShowModal(true);
        }}><MdAdd /> Nouvelle mesure</button>
      </div>

      {/* Growth Chart */}
      {chartData.length > 1 && (
        <div className="chart-container" style={{ marginBottom: 24 }}>
          <div className="chart-header">
            <h3 className="chart-title"><MdTrendingUp style={{ verticalAlign: "middle", marginRight: 8 }} />Courbe de croissance</h3>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="date" stroke="rgba(255,255,255,0.3)" fontSize={12} />
              <YAxis stroke="rgba(255,255,255,0.3)" fontSize={12} />
              <Tooltip contentStyle={{ background: "#1a2736", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 12 }} />
              <Line type="monotone" dataKey="hauteur" stroke="#4ade80" strokeWidth={2} name="Hauteur (cm)" dot={{ r: 4 }} />
              {chartData.some((d) => d.poids) && (
                <Line type="monotone" dataKey="poids" stroke="#fb923c" strokeWidth={2} name="Poids (g)" dot={{ r: 4 }} />
              )}
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {suivis.length > 0 ? (
        <div className="data-table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Cycle</th>
                <th>Hauteur (cm)</th>
                <th>Poids (g)</th>
                <th>Observations</th>
              </tr>
            </thead>
            <tbody>
              {suivis.map((s) => (
                <tr key={s.id_suivi}>
                  <td>{formatDate(s.date_mesure)}</td>
                  <td><span className="badge badge-blue">#{s.id_cycle}</span></td>
                  <td>{s.hauteur_cm != null ? <strong>{s.hauteur_cm}</strong> : "—"}</td>
                  <td>{s.poids_g != null ? <strong>{s.poids_g}</strong> : "—"}</td>
                  <td>{s.observations || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="empty-state">
          <div className="empty-icon">📏</div>
          <h3>Aucune mesure enregistree</h3>
          <p>Ajoutez une mesure de croissance pour suivre l'evolution de vos plantes.</p>
        </div>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Nouvelle mesure</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}><MdClose /></button>
            </div>
            <form onSubmit={handleCreate}>
              <div className="form-row">
                <div className="form-group">
                  <label>Cycle *</label>
                  <select className="form-select" required value={form.id_cycle} onChange={(e) => setForm({ ...form, id_cycle: e.target.value })}>
                    <option value="">Selectionner...</option>
                    {cyclesActifs.map((c) => <option key={c.id_cycle} value={c.id_cycle}>Cycle #{c.id_cycle}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Date *</label>
                  <input className="form-input" type="date" required value={form.date_mesure} onChange={(e) => setForm({ ...form, date_mesure: e.target.value })} />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Hauteur (cm)</label>
                  <input className="form-input" type="number" step="0.1" value={form.hauteur_cm} onChange={(e) => setForm({ ...form, hauteur_cm: e.target.value })} />
                </div>
                <div className="form-group">
                  <label>Poids (g)</label>
                  <input className="form-input" type="number" step="0.1" value={form.poids_g} onChange={(e) => setForm({ ...form, poids_g: e.target.value })} />
                </div>
              </div>
              <div className="form-group">
                <label>Observations</label>
                <textarea className="form-textarea" value={form.observations} onChange={(e) => setForm({ ...form, observations: e.target.value })} placeholder="Ex: feuilles jaunissantes, bonne croissance..." />
              </div>
              <div className="form-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Annuler</button>
                <button type="submit" className="btn btn-primary">Enregistrer</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
