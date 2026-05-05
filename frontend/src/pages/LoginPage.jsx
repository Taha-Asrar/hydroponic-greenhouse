import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './LoginPage.css';

export default function LoginPage() {
  const [isRegister, setIsRegister] = useState(false);
  const [form, setForm] = useState({ nom: '', prenom: '', email: '', mot_de_passe: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (isRegister) {
        await register(form);
        await login(form.email, form.mot_de_passe);
      } else {
        await login(form.email, form.mot_de_passe);
      }
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error || 'Une erreur est survenue');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-bg-pattern" />
      <div className="login-card">
        <div className="login-header">
          <span className="login-logo">🌱</span>
          <h1 className="login-title">HydroSerre</h1>
          <p className="login-subtitle">Serre Hydroponique Intelligente</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <h2 className="login-form-title">
            {isRegister ? 'Créer un compte' : 'Connexion'}
          </h2>

          {error && <div className="login-error">{error}</div>}

          {isRegister && (
            <>
              <div className="login-field">
                <label htmlFor="prenom">Prénom</label>
                <input id="prenom" name="prenom" value={form.prenom} onChange={handleChange} required />
              </div>
              <div className="login-field">
                <label htmlFor="nom">Nom</label>
                <input id="nom" name="nom" value={form.nom} onChange={handleChange} required />
              </div>
            </>
          )}

          <div className="login-field">
            <label htmlFor="email">Email</label>
            <input id="email" name="email" type="email" value={form.email} onChange={handleChange} required />
          </div>

          <div className="login-field">
            <label htmlFor="mot_de_passe">Mot de passe</label>
            <input id="mot_de_passe" name="mot_de_passe" type="password" value={form.mot_de_passe} onChange={handleChange} required />
          </div>

          <button type="submit" className="login-submit" disabled={loading}>
            {loading ? 'Chargement...' : isRegister ? "S'inscrire" : 'Se connecter'}
          </button>

          <p className="login-toggle">
            {isRegister ? 'Déjà un compte ?' : 'Pas encore de compte ?'}{' '}
            <button type="button" onClick={() => { setIsRegister(!isRegister); setError(''); }}>
              {isRegister ? 'Se connecter' : "S'inscrire"}
            </button>
          </p>
        </form>
      </div>
    </div>
  );
}
