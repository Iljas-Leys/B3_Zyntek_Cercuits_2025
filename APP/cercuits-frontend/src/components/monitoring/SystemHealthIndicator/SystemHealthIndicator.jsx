import React from 'react';
import './SystemHealthIndicator.module.css';

const SystemHealthIndicator = ({ status }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
        return 'green';
      case 'warning':
        return 'orange';
      case 'error':
        return 'red';
      default:
        return 'gray';
    }
  };

  return (
    <div className="system-health-indicator">
      <div 
        className="indicator-dot" 
        style={{ backgroundColor: getStatusColor(status) }}
      />
      <span className="status-text">{status || 'Unknown'}</span>
    </div>
  );
};

export default SystemHealthIndicator;
