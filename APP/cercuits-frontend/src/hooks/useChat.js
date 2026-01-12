import { useState } from 'react';

export const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const sendMessage = async (message) => {
    setLoading(true);
    try {
      // TODO: Implement chat message sending logic
      const newMessage = { id: Date.now(), text: message, sender: 'user' };
      setMessages([...messages, newMessage]);
      setLoading(false);
      return newMessage;
    } catch (err) {
      setError(err);
      setLoading(false);
      throw err;
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  return { messages, loading, error, sendMessage, clearChat };
};
