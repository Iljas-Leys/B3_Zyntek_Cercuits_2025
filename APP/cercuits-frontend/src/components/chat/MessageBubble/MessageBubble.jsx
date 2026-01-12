import React from 'react';
import './MessageBubble.module.css';

const MessageBubble = ({ message, sender }) => {
  return (
    <div className={`message-bubble ${sender}`}>
      <p>{message}</p>
    </div>
  );
};

export default MessageBubble;
