import React from 'react';
import './ModelManager.module.css';

const ModelManager = ({ models }) => {
  return (
    <div className="model-manager">
      <h3>Model Manager</h3>
      <ul>
        {models?.map((model, index) => (
          <li key={index}>
            <span>{model.name}</span>
            <span>{model.status}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ModelManager;
