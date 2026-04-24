import { useState, useEffect } from "react";
import { MdDescription, MdDownload, MdAdd, MdClose } from "react-icons/md";
import client from "../api/client";
import "./shared.css";

export default function RapportsPage() {
  const [rapports, setRapports] = useState([]);
  const [cycles, setCycles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [form, setForm] = useState({ id_cycle: "", type: "resume_cycle" });

  useEffect(() => { fetchAll(); }, []);

  const fetchAll = async () => {
    try {
      setLoading(true);
      const [rRes, cRes] = await Promise.all([client.get("/rapports"), client.get("/cycles")]);
      setRapports(rRes.data || []);
      setCycles(cRes.data || []);
    } catch { setError("Impossible de charger les donnees."); }
    finally { setLoading(false); }
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    try {
      setGenerating(true);
      await client.post("/rapports/generer", {
        id_cycle: parseInt(form.id_cycle),
        type: form.type,
      });
      setShowModal(false);
      fetchAll();
    } catch (err) { setError(err.response?.data?.error || "Erreur de generation."); }
    finally { setGenerating(false); }
  };

  const formatDate = (d) => d ? new Date(d).toLocaleDateString("fr-FR", {
    day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit",
  }) : "—";

  const TYPE_LABELS = {
    resume_cycle: "Resume de cycle",
    analyse_capteurs: "Analyse capteurs",
    suivi_croissance: "Suivi croissance",
  };

  if (loading) return <div className="page-loading"><div className="spinner" /><span>Chargement...</span></div>;

  return (
    <div className="crud-page">
      <div className="page-header">
        <h1 className="page-title">Rapports</h1>
        <p className="page-subtitle">Generation et historique des rapports PDF</p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="stats-row">
        <div className="stat-card">
          <div className="stat-label">Rapports generes</div>
          <div className="stat-value" style={{ color: "#3b82f6" }}>{rapports.length}</div>
        </div>
      </div>

      <div className="page-toolbar">
        <div className="toolbar-left" />
        <button className="btn btn-primary" onClick={() => {
          setForm({ id_cycle: cycles[0]?.id_cycle || "", type: "resume_cycle" });
          setShowModal(true);
        }}><MdAdd /> Generer un rapport</button>
      </div>

      {rapports.length > 0 ? (
        <div className="data-table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Type</th>
                <th>Cycle</th>
                <th>Date de generation</th>
                <th>Fichier</th>
                <th style={{ textAlign: "right" }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {rapports.map((r) => (
                <tr key={r.id_rapport}>
                  <td>
                    <MdDescription style={{ verticalAlign: "middle", marginRight: 8, color: "#3b82f6" }} />
                    {TYPE_LABELS[r.type] || r.type}
                  </td>
                  <td><span className="badge badge-blue">Cycle #{r.id_cycle}</span></td>
                  <td>{formatDate(r.date_generation)}</td>
                  <td style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{r.chemin_pdf}</td>
                  <td>
                    <div className="td-actions">
                      <button 
                        className="btn btn-secondary btn-sm" 
                        title="Telecharger"
                        onClick={() => window.open(`http://localhost:5000/${r.chemin_pdf}`, "_blank")}
                      >
                        <MdDownload /> PDF
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="empty-state">
          <div className="empty-icon">📄</div>
          <h3>Aucun rapport</h3>
          <p>Generez un rapport PDF pour un cycle de culture.</p>
          <button className="btn btn-primary" onClick={() => {
            setForm({ id_cycle: cycles[0]?.id_cycle || "", type: "resume_cycle" });
            setShowModal(true);
          }}><MdAdd /> Generer</button>
        </div>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Generer un rapport</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}><MdClose /></button>
            </div>
            <form onSubmit={handleGenerate}>
              <div className="form-group">
                <label>Cycle *</label>
                <select className="form-select" required value={form.id_cycle} onChange={(e) => setForm({ ...form, id_cycle: e.target.value })}>
                  <option value="">Selectionner un cycle...</option>
                  {cycles.map((c) => <option key={c.id_cycle} value={c.id_cycle}>Cycle #{c.id_cycle} — {c.statut}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label>Type de rapport</label>
                <select className="form-select" value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}>
                  <option value="resume_cycle">Resume de cycle</option>
                  <option value="analyse_capteurs">Analyse capteurs</option>
                  <option value="suivi_croissance">Suivi croissance</option>
                </select>
              </div>
              <div className="form-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Annuler</button>
                <button type="submit" className="btn btn-primary" disabled={generating}>
                  {generating ? "Generation..." : "Generer le PDF"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
