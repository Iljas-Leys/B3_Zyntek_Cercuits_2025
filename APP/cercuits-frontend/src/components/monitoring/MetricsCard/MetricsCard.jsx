import React from 'react';
import './MetricsCard.module.css';

const MetricsCard = ({ title, value, unit }) => {
  return (
    <div className="metrics-card">
      <h4>{title}</h4>
      <p className="value">
        {value} <span className="unit">{unit}</span>
      </p>
    </div>
  );
};

export default MetricsCard;
