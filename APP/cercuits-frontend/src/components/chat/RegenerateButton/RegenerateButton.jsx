import React from 'react';
import './RegenerateButton.module.css';

const RegenerateButton = ({ onClick }) => {
  return (
    <button className="regenerate-button" onClick={onClick}>
      Regenerate Response
    </button>
  );
};

export default RegenerateButton;
