import React from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import './MainLayout.css';

export const MainLayout: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('isAuthenticated');
    navigate('/login');
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="logo" onClick={() => navigate('/tickets')} style={{ cursor: 'pointer' }}>
          <img src="/logo_cercuits.png" alt="Logo CERcuits" style={{ height: '50px' }}/>
        </div>
        
        <nav className="nav-items">
          <a 
            href="/knowledge-library" 
            className={`nav-link ${isActive('/knowledge-library') ? 'active' : ''}`}
          >
            Knowledge Library
          </a>
          <a 
            href="/monitor" 
            className={`nav-link ${isActive('/monitor') ? 'active' : ''}`}
          >
            Monitor System
          </a>
          <a 
            href="/testing" 
            className={`nav-link ${isActive('/testing') ? 'active' : ''}`}
          >
            Testing
          </a>
          <a 
            href="/tickets" 
            className={`nav-link ${isActive('/tickets') ? 'active' : ''}`}
          >
            Agent TSE
          </a>
          
          <div className="notification-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
              <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
            </svg>
          </div>
          
          <div className="user-avatar" onClick={handleLogout} title="Logout"></div>
        </nav>
      </header>
      
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
};