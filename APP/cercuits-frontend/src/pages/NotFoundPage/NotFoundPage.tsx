import React from 'react';
import { useNavigate } from 'react-router-dom';
import './NotFoundPage.css';

export const NotFoundPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="not-found-container">
      <div className="not-found-content">
        <div className="not-found-icon">404</div>
        <h1 className="not-found-title">Page Not Found</h1>
        <p className="not-found-text">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <button className="not-found-button" onClick={() => navigate('/tickets')}>
          Back to Tickets
        </button>
      </div>
    </div>
  );
};