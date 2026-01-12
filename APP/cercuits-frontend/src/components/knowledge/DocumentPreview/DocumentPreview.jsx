import React from 'react';
import './DocumentPreview.module.css';

const DocumentPreview = ({ document }) => {
  return (
    <div className="document-preview">
      <h3>Document Preview</h3>
      <div className="preview-content">
        <p>{document?.content || 'No preview available'}</p>
      </div>
    </div>
  );
};

export default DocumentPreview;
