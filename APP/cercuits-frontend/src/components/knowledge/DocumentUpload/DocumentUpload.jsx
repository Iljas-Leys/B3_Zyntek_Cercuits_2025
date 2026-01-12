import React, { useState } from 'react';
import './DocumentUpload.module.css';

const DocumentUpload = ({ onUpload }) => {
  const [file, setFile] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (file && onUpload) {
      onUpload(file);
    }
  };

  return (
    <div className="document-upload">
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleFileChange} />
        <button type="submit">Upload</button>
      </form>
    </div>
  );
};

export default DocumentUpload;
