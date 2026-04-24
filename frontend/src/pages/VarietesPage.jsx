import { useState, useEffect } from "react";
import { MdAdd, MdEdit, MdDelete, MdClose, MdGrass } from "react-icons/md";
import client from "../api/client";
import "./shared.css";

export default function VarietesPage() {
  const [varietes, setVarietes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ nom: "", description: "", duree_croissance_jours: "" });
  const [search, setSearch] = useState("");

  useEffect(() => { fetchVarietes(); }, []);

  const fetchVarietes = async () => {
    try {
      setLoading(true);
      const res = await client.get("/varietes");
      setVarietes(res.data || []);
    } catch { setError("Impossible de charger les varietes."); }
    finally { setLoading(false); }
  };

  const openCreate = () => {
    setEditing(null);
    setForm({ nom: "", description: "", duree_croissance_jours: "" });
    setShowModal(true);
  };

  const openEdit = (v) => {
    setEditing(v);
    setForm({ nom: v.nom, description: v.description || "", duree_croissance_jours: v.duree_croissance_jours || "" });
    setShowModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = { ...form, duree_croissance_jours: parseInt(form.duree_croissance_jours) || 0 };
      if (editing) {
        await client.put(`/varietes/${editing.id_variete}`, payload);
      } else {
        await client.post("/varietes", payload);
      }
      setShowModal(false);
      fetchVarietes();
    } catch (err) {
      setError(err.response?.data?.error || "Erreur lors de la sauvegarde.");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Supprimer cette variete ?")) return;
    try {
      await client.delete(`/varietes/${id}`);
      fetchVarietes();
    } catch { setError("Erreur lors de la suppression."); }
  };

  const filtered = varietes.filter((v) =>
    v.nom.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) return <div className="page-loading"><div className="spinner" /><span>Chargement...</span></div>;

  return (
    <div className="crud-page">
      <div className="page-header">
        <h1 className="page-title">Varietes de Plantes</h1>
        <p className="page-subtitle">Catalogue des plantes cultivables en hydroponie</p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="page-toolbar">
        <div className="toolbar-left">
          <input className="search-input" placeholder="Rechercher une variete..." value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
        <button className="btn btn-primary" onClick={openCreate}><MdAdd /> Ajouter</button>
      </div>

      {filtered.length > 0 ? (
        <div className="data-table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Nom</th>
                <th>Description</th>
                <th>Duree (jours)</th>
                <th style={{ textAlign: "right" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((v) => (
                <tr key={v.id_variete}>
                  <td><MdGrass style={{ verticalAlign: "middle", marginRight: 8, color: "#4ade80" }} />{v.nom}</td>
                  <td>{v.description || "—"}</td>
                  <td><span className="badge badge-green">{v.duree_croissance_jours} jours</span></td>
                  <td>
                    <div className="td-actions">
                      <button className="btn-icon" onClick={() => openEdit(v)} title="Modifier"><MdEdit /></button>
                      <button className="btn-icon danger" onClick={() => handleDelete(v.id_variete)} title="Supprimer"><MdDelete /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="empty-state">
          <div className="empty-icon">🌱</div>
          <h3>Aucune variete trouvee</h3>
          <p>Ajoutez votre premiere variete de plante pour commencer.</p>
          <button className="btn btn-primary" onClick={openCreate}><MdAdd /> Ajouter une variete</button>
        </div>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editing ? "Modifier la variete" : "Nouvelle variete"}</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}><MdClose /></button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Nom *</label>
                <input className="form-input" required value={form.nom} onChange={(e) => setForm({ ...form, nom: e.target.value })} />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea className="form-textarea" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
              </div>
              <div className="form-group">
                <label>Duree de croissance (jours) *</label>
                <input className="form-input" type="number" required value={form.duree_croissance_jours} onChange={(e) => setForm({ ...form, duree_croissance_jours: e.target.value })} />
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
