import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Layout from './components/Layout/Layout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import VarietesPage from './pages/VarietesPage';
import RecettesPage from './pages/RecettesPage';
import CyclesPage from './pages/CyclesPage';
import CapteursPage from './pages/CapteursPage';
import AlertesPage from './pages/AlertesPage';
import SuiviPage from './pages/SuiviPage';
import RapportsPage from './pages/RapportsPage';
import SettingsPage from './pages/SettingsPage';
import './App.css';

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) return <div className="loading-screen">Chargement...</div>;
  if (!user) return <Navigate to="/login" replace />;

  return children;
};

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="cycles" element={<CyclesPage />} />
        <Route path="varietes" element={<VarietesPage />} />
        <Route path="recettes" element={<RecettesPage />} />
        <Route path="capteurs" element={<CapteursPage />} />
        <Route path="alertes" element={<AlertesPage />} />
        <Route path="suivi" element={<SuiviPage />} />
        <Route path="rapports" element={<RapportsPage />} />
        <Route path="parametres" element={<SettingsPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
