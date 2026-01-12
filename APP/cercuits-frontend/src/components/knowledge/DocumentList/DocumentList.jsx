import React from 'react';
import './DocumentList.module.css';

const DocumentList = ({ documents }) => {
  return (
    <div className="document-list">
      <h2>Documents</h2>
      <ul>
        {documents?.map((doc, index) => (
          <li key={index}>{doc.name}</li>
        ))}
      </ul>
    </div>
  );
};

export default DocumentList;
