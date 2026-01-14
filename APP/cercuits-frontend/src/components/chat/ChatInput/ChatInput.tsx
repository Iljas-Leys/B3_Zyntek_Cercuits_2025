import React, { useState, useRef, useEffect } from 'react';
import './ChatInput.css';

interface ChatInputProps {
  onSendMessage: (message: string, attachedDocs: string[]) => void;
  onOpenKnowledgeBase: () => void;
  attachedDocuments: Array<{ id: string; title: string }>;
  onRemoveDocument: (id: string) => void;
  disabled?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  onOpenKnowledgeBase,
  attachedDocuments,
  onRemoveDocument,
  disabled = false,
}) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 120) + 'px';
    }
  }, [message]);

  const handleSend = () => {
    if (message.trim() || attachedDocuments.length > 0) {
      onSendMessage(
        message.trim(),
        attachedDocuments.map((doc) => doc.id)
      );
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-input-container">
      {attachedDocuments.length > 0 && (
        <div className="attachment-badges">
          {attachedDocuments.map((doc) => (
            <div key={doc.id} className="attachment-badge">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
              </svg>
              <span>{doc.title}</span>
              <button
                className="remove-badge"
                onClick={() => onRemoveDocument(doc.id)}
                aria-label="Remove document"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="input-wrapper">
        <button
          className="tool-button"
          onClick={onOpenKnowledgeBase}
          title="Attach from Knowledge Base"
          disabled={disabled}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path>
          </svg>
        </button>

        <textarea
          ref={textareaRef}
          className="chat-input"
          placeholder="Ask follow-up questions or provide instructions..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          rows={1}
        />

        <button
          className="send-button"
          onClick={handleSend}
          disabled={disabled || (!message.trim() && attachedDocuments.length === 0)}
          title="Send message"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </div>
    </div>
  );
};