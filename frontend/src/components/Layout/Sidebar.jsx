import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  MdDashboard,
  MdGrass,
  MdMenuBook,
  MdLoop,
  MdSensors,
  MdNotifications,
  MdTrendingUp,
  MdDescription,
  MdSettings,
  MdLogout,
} from 'react-icons/md';
import './Sidebar.css';

const navItems = [
  { path: '/', icon: <MdDashboard />, label: 'Dashboard' },
  { path: '/cycles', icon: <MdLoop />, label: 'Cycles' },
  { path: '/varietes', icon: <MdGrass />, label: 'Variétés' },
  { path: '/recettes', icon: <MdMenuBook />, label: 'Recettes' },
  { path: '/capteurs', icon: <MdSensors />, label: 'Capteurs' },
  { path: '/alertes', icon: <MdNotifications />, label: 'Alertes' },
  { path: '/suivi', icon: <MdTrendingUp />, label: 'Suivi' },
  { path: '/rapports', icon: <MdDescription />, label: 'Rapports' },
  { path: '/parametres', icon: <MdSettings />, label: 'Paramètres' },
];

export default function Sidebar() {
  const { user, logout } = useAuth();

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <span className="sidebar-logo">🌱</span>
        <h2 className="sidebar-title">HydroSerre</h2>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `sidebar-link ${isActive ? 'sidebar-link--active' : ''}`
            }
            end={item.path === '/'}
          >
            <span className="sidebar-link-icon">{item.icon}</span>
            <span className="sidebar-link-label">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-user">
          <div className="sidebar-user-avatar">
            {user?.prenom?.[0]}{user?.nom?.[0]}
          </div>
          <div className="sidebar-user-info">
            <span className="sidebar-user-name">{user?.prenom} {user?.nom}</span>
            <span className="sidebar-user-role">{user?.role}</span>
          </div>
        </div>
        <button className="sidebar-logout" onClick={logout} title="Déconnexion">
          <MdLogout />
        </button>
      </div>
    </aside>
  );
}
