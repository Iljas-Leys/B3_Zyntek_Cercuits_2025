import React from 'react';
import './SourceDocumentList.module.css';

const SourceDocumentList = ({ documents }) => {
  return (
    <div className="source-document-list">
      <h3>Source Documents</h3>
      <ul>
        {documents?.map((doc, index) => (
          <li key={index}>{doc.name}</li>
        ))}
      </ul>
    </div>
  );
};

export default SourceDocumentList;
