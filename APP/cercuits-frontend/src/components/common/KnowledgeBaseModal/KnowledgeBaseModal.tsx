import React, { useState } from 'react';
import { KnowledgeDocument } from '../../../types/aiResponse';
import './KnowledgeBaseModal.css';

interface KnowledgeBaseModalProps {
  isOpen: boolean;
  onClose: () => void;
  documents: KnowledgeDocument[];
  onSelectDocument: (document: KnowledgeDocument) => void;
}

export const KnowledgeBaseModal: React.FC<KnowledgeBaseModalProps> = ({
  isOpen,
  onClose,
  documents,
  onSelectDocument,
}) => {
  const [searchQuery, setSearchQuery] = useState('');

  if (!isOpen) return null;

  const filteredDocuments = documents.filter((doc) =>
    doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    doc.category?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getFileIcon = (fileType: string) => {
    switch (fileType) {
      case 'pdf':
        return '📄';
      case 'docx':
        return '📘';
      case 'txt':
        return '📋';
      case 'xlsx':
        return '📊';
      default:
        return '📄';
    }
  };

  const handleSelectDocument = (doc: KnowledgeDocument) => {
    onSelectDocument(doc);
    onClose();
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="kb-modal-overlay" onClick={handleBackdropClick}>
      <div className="kb-modal-content">
        <div className="kb-modal-header">
          <h3>Attach from Knowledge Base</h3>
          <button className="kb-close-button" onClick={onClose} aria-label="Close modal">
            ×
          </button>
        </div>

        <div className="kb-search">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.35-4.35"></path>
          </svg>
          <input
            type="text"
            placeholder="Search documents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="kb-search-input"
            autoFocus
          />
        </div>

        <div className="kb-document-list">
          {filteredDocuments.length > 0 ? (
            filteredDocuments.map((doc) => (
              <div
                key={doc.id}
                className="kb-document-item"
                onClick={() => handleSelectDocument(doc)}
              >
                <div className="kb-doc-icon">{getFileIcon(doc.fileType)}</div>
                <div className="kb-doc-info">
                  <div className="kb-doc-title">{doc.title}</div>
                  <div className="kb-doc-meta">
                    <span className="kb-doc-type">{doc.fileType.toUpperCase()}</span>
                    <span className="kb-doc-separator">•</span>
                    <span className="kb-doc-size">{doc.fileSize}</span>
                    {doc.category && (
                      <>
                        <span className="kb-doc-separator">•</span>
                        <span className="kb-doc-category">{doc.category}</span>
                      </>
                    )}
                  </div>
                </div>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="9 18 15 12 9 6"></polyline>
                </svg>
              </div>
            ))
          ) : (
            <div className="kb-empty-state">
              <div className="kb-empty-icon">🔍</div>
              <div className="kb-empty-text">No documents found</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};