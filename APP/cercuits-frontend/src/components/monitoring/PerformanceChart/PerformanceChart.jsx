import React from 'react';
import './PerformanceChart.module.css';

const PerformanceChart = ({ data }) => {
  return (
    <div className="performance-chart">
      <h3>Performance Chart</h3>
      <div className="chart-placeholder">
        Chart visualization goes here
      </div>
    </div>
  );
};

export default PerformanceChart;
