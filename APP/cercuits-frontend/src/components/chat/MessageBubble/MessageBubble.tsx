import React from 'react';
import { ChatMessage, MessageSender } from '../../../types/chat';
import './MessageBubble.css';

interface MessageBubbleProps {
  message: ChatMessage;
  customerName?: string;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message, customerName }) => {
  const isUser = message.sender === MessageSender.USER;
  const displayName = isUser ? (customerName || 'Customer') : 'AI Assistant';
  const initials = isUser ? (customerName?.split(' ').map(n => n[0]).join('') || 'U') : 'AI';
  
  const formatTime = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 1) return 'just now';
    if (minutes < 60) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className={`message-bubble ${isUser ? 'message-user' : 'message-ai'}`}>
      <div className={`message-avatar ${isUser ? 'avatar-user' : 'avatar-ai'}`}>
        {initials}
      </div>
      <div className="message-content-wrapper">
        <div className="message-header">
          <span className="message-author">{displayName}</span>
          <span className="message-time">{formatTime(message.timestamp)}</span>
        </div>
        <div className="message-text">
          {message.content}
        </div>
      </div>
    </div>
  );
};