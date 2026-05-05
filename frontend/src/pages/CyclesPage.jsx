import { useState, useEffect } from "react";
import { MdAdd, MdClose, MdLoop, MdCheck, MdCancel, MdPlayArrow } from "react-icons/md";
import client from "../api/client";
import "./shared.css";

const STATUS_MAP = {
  en_cours:  { label: "En cours",  badge: "badge-green" },
  termine:   { label: "Termine",   badge: "badge-blue" },
  abandonne: { label: "Abandonne", badge: "badge-red" },
};

export default function CyclesPage() {
  const [cycles, setCycles] = useState([]);
  const [varietes, setVarietes] = useState([]);
  const [recettes, setRecettes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [filterStatut, setFilterStatut] = useState("");
  const [form, setForm] = useState({ id_variete: "", id_recette: "", notes: "" });

  useEffect(() => { fetchAll(); }, []);

  const fetchAll = async () => {
    try {
      setLoading(true);
      const [cRes, vRes, rRes] = await Promise.all([
        client.get("/cycles"), client.get("/varietes"), client.get("/recettes"),
      ]);
      setCycles(cRes.data || []);
      setVarietes(vRes.data || []);
      setRecettes(rRes.data || []);
    } catch { setError("Impossible de charger les donnees."); }
    finally { setLoading(false); }
  };

  const openCreate = () => {
    setForm({ id_variete: varietes[0]?.id_variete || "", id_recette: recettes[0]?.id_recette || "", notes: "" });
    setShowModal(true);
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await client.post("/cycles", {
        id_variete: parseInt(form.id_variete),
        id_recette: parseInt(form.id_recette),
        notes: form.notes || undefined,
      });
      setShowModal(false);
      fetchAll();
    } catch (err) { setError(err.response?.data?.error || "Erreur."); }
  };

  const terminerCycle = async (id) => {
    if (!window.confirm("Terminer ce cycle ?")) return;
    try { await client.patch(`/cycles/${id}/terminer`); fetchAll(); }
    catch (err) { setError(err.response?.data?.error || "Erreur."); }
  };

  const abandonnerCycle = async (id) => {
    if (!window.confirm("Abandonner ce cycle ?")) return;
    try { await client.patch(`/cycles/${id}/abandonner`); fetchAll(); }
    catch (err) { setError(err.response?.data?.error || "Erreur."); }
  };

  const getVarieteNom = (id) => varietes.find((v) => v.id_variete === id)?.nom || "—";
  const getRecetteNom = (id) => recettes.find((r) => r.id_recette === id)?.nom_recette || "—";
  const formatDate = (d) => d ? new Date(d).toLocaleDateString("fr-FR") : "—";

  const filtered = cycles.filter((c) => filterStatut ? c.statut === filterStatut : true);

  // Stats
  const enCours = cycles.filter((c) => c.statut === "en_cours").length;
  const termines = cycles.filter((c) => c.statut === "termine").length;

  if (loading) return <div className="page-loading"><div className="spinner" /><span>Chargement...</span></div>;

  return (
    <div className="crud-page">
      <div className="page-header">
        <h1 className="page-title">Cycles de Culture</h1>
        <p className="page-subtitle">Gerez le cycle de vie de vos cultures</p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="stats-row">
        <div className="stat-card">
          <div className="stat-label">Cycles actifs</div>
          <div className="stat-value" style={{ color: "#4ade80" }}>{enCours}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Cycles termines</div>
          <div className="stat-value" style={{ color: "#3b82f6" }}>{termines}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total</div>
          <div className="stat-value">{cycles.length}</div>
        </div>
      </div>

      <div className="page-toolbar">
        <div className="toolbar-left">
          <select className="filter-select" value={filterStatut} onChange={(e) => setFilterStatut(e.target.value)}>
            <option value="">Tous les statuts</option>
            <option value="en_cours">En cours</option>
            <option value="termine">Termine</option>
            <option value="abandonne">Abandonne</option>
          </select>
        </div>
        <button className="btn btn-primary" onClick={openCreate}><MdAdd /> Nouveau cycle</button>
      </div>

      {filtered.length > 0 ? (
        <div className="data-table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Variete</th>
                <th>Recette</th>
                <th>Debut</th>
                <th>Fin prevue</th>
                <th>Statut</th>
                <th style={{ textAlign: "right" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((c) => {
                const st = STATUS_MAP[c.statut] || { label: c.statut, badge: "badge-gray" };
                return (
                  <tr key={c.id_cycle}>
                    <td><MdLoop style={{ verticalAlign: "middle", marginRight: 8, color: "#22d3ee" }} />{getVarieteNom(c.id_variete)}</td>
                    <td>{getRecetteNom(c.id_recette)}</td>
                    <td>{formatDate(c.date_debut)}</td>
                    <td>{formatDate(c.date_fin_prevue)}</td>
                    <td><span className={`badge ${st.badge}`}>{st.label}</span></td>
                    <td>
                      <div className="td-actions">
                        {c.statut === "en_cours" && (
                          <>
                            <button className="btn btn-success btn-sm" onClick={() => terminerCycle(c.id_cycle)} title="Terminer"><MdCheck /> Terminer</button>
                            <button className="btn btn-danger btn-sm" onClick={() => abandonnerCycle(c.id_cycle)} title="Abandonner"><MdCancel /></button>
                          </>
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
          <div className="empty-icon">🔄</div>
          <h3>Aucun cycle</h3>
          <p>Demarrez un nouveau cycle de culture.</p>
          <button className="btn btn-primary" onClick={openCreate}><MdPlayArrow /> Demarrer un cycle</button>
        </div>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Nouveau cycle de culture</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}><MdClose /></button>
            </div>
            <form onSubmit={handleCreate}>
              <div className="form-group">
                <label>Variete *</label>
                <select className="form-select" required value={form.id_variete} onChange={(e) => setForm({ ...form, id_variete: e.target.value })}>
                  <option value="">Selectionner...</option>
                  {varietes.map((v) => <option key={v.id_variete} value={v.id_variete}>{v.nom}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label>Recette *</label>
                <select className="form-select" required value={form.id_recette} onChange={(e) => setForm({ ...form, id_recette: e.target.value })}>
                  <option value="">Selectionner...</option>
                  {recettes.map((r) => <option key={r.id_recette} value={r.id_recette}>{r.nom_recette}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label>Notes</label>
                <textarea className="form-textarea" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} placeholder="Notes optionnelles..." />
              </div>
              <div className="form-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Annuler</button>
                <button type="submit" className="btn btn-primary"><MdPlayArrow /> Demarrer</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
