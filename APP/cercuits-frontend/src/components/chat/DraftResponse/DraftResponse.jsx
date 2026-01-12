import React from 'react';
import './DraftResponse.module.css';

const DraftResponse = ({ draft }) => {
  return (
    <div className="draft-response">
      <h3>Draft Response</h3>
      <p>{draft}</p>
    </div>
  );
};

export default DraftResponse;
