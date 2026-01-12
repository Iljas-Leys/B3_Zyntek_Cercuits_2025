const API_BASE_URL = 'http://localhost:8000/api';

export const api = {
  getEmails: async () => {
    const response = await fetch(`${API_BASE_URL}/emails`);
    return response.json();
  },
  
  createChatSession: async (emailId: number) => {
    const response = await fetch(
      `${API_BASE_URL}/emails/${emailId}/chat-session`, 
      { method: 'POST' }
    );
    return response.json();
  },
  
  generateDraft: async (sessionId: number) => {
    const response = await fetch(
      `${API_BASE_URL}/chat-sessions/${sessionId}/generate-draft`, 
      { method: 'POST' }
    );
    return response.json();
  },
};