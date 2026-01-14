import React, { useState } from 'react';
import { DraftResponse } from '../../../types/chat';
import { AIModel } from '../../../types/aiResponse';
import './AIResponseBox.css';

interface AIResponseBoxProps {
  draft: DraftResponse;
  availableModels: AIModel[];
  onRegenerate: (modelId?: string) => void;
  onAccept: () => void;
  onRateResponse: (rating: number) => void;
  currentRating?: number;
}

export const AIResponseBox: React.FC<AIResponseBoxProps> = ({
  draft,
  availableModels,
  onRegenerate,
  onAccept,
  onRateResponse,
  currentRating = 0,
}) => {
  const [selectedModel, setSelectedModel] = useState(availableModels[0]?.id || '');
  const [hoveredStar, setHoveredStar] = useState(0);
  const [isRegenerating, setIsRegenerating] = useState(false);

  const handleModelChange = (modelId: string) => {
    setSelectedModel(modelId);
  };

  const handleRegenerate = async () => {
    setIsRegenerating(true);
    await onRegenerate(selectedModel);
    setIsRegenerating(false);
  };

  const handleStarClick = (rating: number) => {
    onRateResponse(rating);
  };

  const renderStars = () => {
    return [1, 2, 3, 4, 5].map((star) => (
      <svg
        key={star}
        className={`star ${star <= (hoveredStar || currentRating) ? 'star-active' : ''}`}
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill={star <= (hoveredStar || currentRating) ? '#fbbf24' : 'none'}
        stroke="currentColor"
        strokeWidth="2"
        onClick={() => handleStarClick(star)}
        onMouseEnter={() => setHoveredStar(star)}
        onMouseLeave={() => setHoveredStar(0)}
        style={{ cursor: 'pointer' }}
      >
        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
      </svg>
    ));
  };

  // Parse markdown-like content to HTML
  const formatContent = (content: string) => {
    return content.split('\n').map((line, index) => {
      // Headers
      if (line.startsWith('**') && line.endsWith('**')) {
        return <h4 key={index}>{line.replace(/\*\*/g, '')}</h4>;
      }
      // Bold
      if (line.includes('**')) {
        const parts = line.split('**');
        return (
          <p key={index}>
            {parts.map((part, i) => (i % 2 === 1 ? <strong key={i}>{part}</strong> : part))}
          </p>
        );
      }
      // List items
      if (line.trim().startsWith('-')) {
        return <li key={index}>{line.replace(/^-\s*/, '')}</li>;
      }
      // Regular paragraph
      if (line.trim()) {
        return <p key={index}>{line}</p>;
      }
      return <br key={index} />;
    });
  };

  return (
    <div className="ai-response-box">
      <div className="ai-response-header">
        <div className="ai-response-header-left">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"></circle>
            <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
          </svg>
          AI GENERATED RESPONSE
        </div>
        <select
          className="model-selector"
          value={selectedModel}
          onChange={(e) => handleModelChange(e.target.value)}
        >
          {availableModels.map((model) => (
            <option key={model.id} value={model.id}>
              {model.displayName}
            </option>
          ))}
        </select>
      </div>

      <div className="ai-response-content">
        <div className="response-text">
          {formatContent(draft.content)}
        </div>

        {draft.sourceDocuments && draft.sourceDocuments.length > 0 && (
          <div className="source-documents">
            <h5>Source Documents Used:</h5>
            <div className="source-list">
              {draft.sourceDocuments.map((doc) => (
                <div key={doc.id} className="source-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                  </svg>
                  <span className="source-name">{doc.name}</span>
                  <span className="source-score">{Math.round(doc.relevanceScore * 100)}% match</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="rating-container">
          <span className="rating-label">Rate this response:</span>
          <div className="star-rating">{renderStars()}</div>
          {currentRating > 0 && (
            <span className="rating-feedback">Thanks for feedback!</span>
          )}
        </div>
      </div>

      <div className="action-buttons">
        <button
          className="btn btn-regenerate"
          onClick={handleRegenerate}
          disabled={isRegenerating}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M23 4v6h-6"></path>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
          </svg>
          {isRegenerating ? 'Regenerating...' : 'Regenerate'}
        </button>
        <button className="btn btn-accept" onClick={onAccept}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
          Accept & Edit
        </button>
      </div>
    </div>
  );
};