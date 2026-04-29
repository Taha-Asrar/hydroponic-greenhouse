import { useState, useEffect } from "react";
import { MdAdd, MdEdit, MdDelete, MdClose, MdMenuBook } from "react-icons/md";
import client from "../api/client";
import "./shared.css";

export default function RecettesPage() {
  const [recettes, setRecettes] = useState([]);
  const [varietes, setVarietes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState(null);
  const [filterVariete, setFilterVariete] = useState("");
  const [form, setForm] = useState({
    nom_recette: "", id_variete: "", phase: "",
    temp_eau_min: "", temp_eau_max: "",
    temp_air_min: "", temp_air_max: "", humidite_min: "", humidite_max: "",
    luminosite_min: "", luminosite_max: "", luminosite_heures_jour: "", niveau_eau_min: "",
  });

  useEffect(() => { fetchAll(); }, []);

  const fetchAll = async () => {
    try {
      setLoading(true);
      const [rRes, vRes] = await Promise.all([client.get("/recettes"), client.get("/varietes")]);
      setRecettes(rRes.data || []);
      setVarietes(vRes.data || []);
    } catch { setError("Impossible de charger les donnees."); }
    finally { setLoading(false); }
  };

  const openCreate = () => {
    setEditing(null);
    setForm({
      nom_recette: "", id_variete: varietes[0]?.id_variete || "", phase: "",
      temp_eau_min: "", temp_eau_max: "",
      temp_air_min: "", temp_air_max: "", humidite_min: "", humidite_max: "",
      luminosite_min: "", luminosite_max: "", luminosite_heures_jour: "", niveau_eau_min: "",
    });
    setShowModal(true);
  };

  const openEdit = (r) => {
    setEditing(r);
    setForm({
      nom_recette: r.nom_recette || "", id_variete: r.id_variete || "",
      phase: r.phase || "",
      temp_eau_min: r.temp_eau_min ?? "", temp_eau_max: r.temp_eau_max ?? "",
      temp_air_min: r.temp_air_min ?? "", temp_air_max: r.temp_air_max ?? "",
      humidite_min: r.humidite_min ?? "", humidite_max: r.humidite_max ?? "",
      luminosite_min: r.luminosite_min ?? "", luminosite_max: r.luminosite_max ?? "",
      luminosite_heures_jour: r.luminosite_heures_jour ?? "", niveau_eau_min: r.niveau_eau_min ?? "",
    });
    setShowModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {};
      Object.entries(form).forEach(([k, v]) => {
        if (v !== "" && v !== null) {
          payload[k] = ["id_variete", "luminosite_heures_jour"].includes(k) ? parseInt(v) : isNaN(v) ? v : parseFloat(v);
        }
      });
      if (editing) {
        await client.put(`/recettes/${editing.id_recette}`, payload);
      } else {
        await client.post("/recettes", payload);
      }
      setShowModal(false);
      fetchAll();
    } catch (err) { setError(err.response?.data?.error || "Erreur de sauvegarde."); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Supprimer cette recette ?")) return;
    try { await client.delete(`/recettes/${id}`); fetchAll(); }
    catch { setError("Erreur lors de la suppression."); }
  };

  const getVarieteNom = (id) => varietes.find((v) => v.id_variete === id)?.nom || "—";

  const filtered = recettes.filter((r) =>
    filterVariete ? r.id_variete === parseInt(filterVariete) : true
  );

  if (loading) return <div className="page-loading"><div className="spinner" /><span>Chargement...</span></div>;

  return (
    <div className="crud-page">
      <div className="page-header">
        <h1 className="page-title">Recettes de Culture</h1>
        <p className="page-subtitle">Parametres ideaux pour chaque phase de croissance</p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="page-toolbar">
        <div className="toolbar-left">
          <select className="filter-select" value={filterVariete} onChange={(e) => setFilterVariete(e.target.value)}>
            <option value="">Toutes les varietes</option>
            {varietes.map((v) => <option key={v.id_variete} value={v.id_variete}>{v.nom}</option>)}
          </select>
        </div>
        <button className="btn btn-primary" onClick={openCreate}><MdAdd /> Nouvelle recette</button>
      </div>

      {filtered.length > 0 ? (
        <div className="data-table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Nom</th>
                <th>Variete</th>
                <th>Phase</th>
                <th>Temp. Air (°C)</th>
                <th>Temp. Eau (°C)</th>
                <th>Humidite (%)</th>
                <th style={{ textAlign: "right" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((r) => (
                <tr key={r.id_recette}>
                  <td><MdMenuBook style={{ verticalAlign: "middle", marginRight: 8, color: "#a855f7" }} />{r.nom_recette}</td>
                  <td>{getVarieteNom(r.id_variete)}</td>
                  <td>{r.phase ? <span className="badge badge-blue">{r.phase}</span> : "—"}</td>
                  <td>{r.temp_air_min != null ? `${r.temp_air_min} - ${r.temp_air_max}` : "—"}</td>
                  <td>{r.temp_eau_min != null ? `${r.temp_eau_min} - ${r.temp_eau_max}` : "—"}</td>
                  <td>{r.humidite_min != null ? `${r.humidite_min} - ${r.humidite_max}` : "—"}</td>
                  <td>
                    <div className="td-actions">
                      <button className="btn-icon" onClick={() => openEdit(r)} title="Modifier"><MdEdit /></button>
                      <button className="btn-icon danger" onClick={() => handleDelete(r.id_recette)} title="Supprimer"><MdDelete /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="empty-state">
          <div className="empty-icon">📋</div>
          <h3>Aucune recette configuree</h3>
          <p>Creez une recette de culture avec les parametres ideaux pour vos plantes.</p>
          <button className="btn btn-primary" onClick={openCreate}><MdAdd /> Creer une recette</button>
        </div>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 640 }}>
            <div className="modal-header">
              <h2>{editing ? "Modifier la recette" : "Nouvelle recette"}</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}><MdClose /></button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-row">
                <div className="form-group">
                  <label>Nom de la recette *</label>
                  <input className="form-input" required value={form.nom_recette} onChange={(e) => setForm({ ...form, nom_recette: e.target.value })} />
                </div>
                <div className="form-group">
                  <label>Variete *</label>
                  <select className="form-select" required value={form.id_variete} onChange={(e) => setForm({ ...form, id_variete: e.target.value })}>
                    <option value="">Selectionner...</option>
                    {varietes.map((v) => <option key={v.id_variete} value={v.id_variete}>{v.nom}</option>)}
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label>Phase (ex: germination, croissance, floraison)</label>
                <input className="form-input" value={form.phase} onChange={(e) => setForm({ ...form, phase: e.target.value })} />
              </div>

              <div className="form-row">
                <div className="form-group"><label>Temp. Eau Min (°C)</label><input className="form-input" type="number" step="0.1" value={form.temp_eau_min} onChange={(e) => setForm({ ...form, temp_eau_min: e.target.value })} /></div>
                <div className="form-group"><label>Temp. Eau Max (°C)</label><input className="form-input" type="number" step="0.1" value={form.temp_eau_max} onChange={(e) => setForm({ ...form, temp_eau_max: e.target.value })} /></div>
              </div>
              <div className="form-row">
                <div className="form-group"><label>Temp. Air Min (°C)</label><input className="form-input" type="number" step="0.1" value={form.temp_air_min} onChange={(e) => setForm({ ...form, temp_air_min: e.target.value })} /></div>
                <div className="form-group"><label>Temp. Air Max (°C)</label><input className="form-input" type="number" step="0.1" value={form.temp_air_max} onChange={(e) => setForm({ ...form, temp_air_max: e.target.value })} /></div>
              </div>
              <div className="form-row">
                <div className="form-group"><label>Humidite Min (%)</label><input className="form-input" type="number" step="1" value={form.humidite_min} onChange={(e) => setForm({ ...form, humidite_min: e.target.value })} /></div>
                <div className="form-group"><label>Humidite Max (%)</label><input className="form-input" type="number" step="1" value={form.humidite_max} onChange={(e) => setForm({ ...form, humidite_max: e.target.value })} /></div>
              </div>
              <div className="form-row">
                <div className="form-group"><label>Luminosite Min (lux)</label><input className="form-input" type="number" value={form.luminosite_min} onChange={(e) => setForm({ ...form, luminosite_min: e.target.value })} /></div>
                <div className="form-group"><label>Luminosite Max (lux)</label><input className="form-input" type="number" value={form.luminosite_max} onChange={(e) => setForm({ ...form, luminosite_max: e.target.value })} /></div>
              </div>
              <div className="form-row">
                <div className="form-group"><label>Eclairage (h/jour)</label><input className="form-input" type="number" value={form.luminosite_heures_jour} onChange={(e) => setForm({ ...form, luminosite_heures_jour: e.target.value })} /></div>
                <div className="form-group"><label>Niveau eau min (cm)</label><input className="form-input" type="number" step="0.1" value={form.niveau_eau_min} onChange={(e) => setForm({ ...form, niveau_eau_min: e.target.value })} /></div>
              </div>
              <div className="form-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Annuler</button>
                <button type="submit" className="btn btn-primary">{editing ? "Sauvegarder" : "Creer"}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
