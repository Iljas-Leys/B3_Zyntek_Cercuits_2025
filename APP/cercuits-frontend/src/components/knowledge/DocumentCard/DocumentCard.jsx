import React from 'react';
import './DocumentCard.module.css';

const DocumentCard = ({ document }) => {
  return (
    <div className="document-card">
      <h3>{document?.name}</h3>
      <p>{document?.description}</p>
    </div>
  );
};

export default DocumentCard;
