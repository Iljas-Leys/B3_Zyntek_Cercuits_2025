import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { MessageBubble } from '../../components/chat/MessageBubble/MessageBubble';
import { AIResponseBox } from '../../components/chat/AIResponseBox/AIResponseBox';
import { ChatInput } from '../../components/chat/ChatInput/ChatInput';
import { TicketSidebar } from '../../components/email/TicketSidebar/TicketSidebar';
import { KnowledgeBaseModal } from '../../components/common/KnowledgeBaseModal/KnowledgeBaseModal';
import { 
  mockAIResponseData, 
  mockKnowledgeDocuments, 
  generateMockAIResponse 
} from '../../types/mockAIResponseData';
import { ChatMessage, MessageSender } from '../../types/chat';
import { KnowledgeDocument } from '../../types/aiResponse';
import './AIResponsePage.css';

export const AIResponsePage: React.FC = () => {
  const navigate = useNavigate();
  const { emailId } = useParams<{ emailId: string }>();
  const conversationRef = useRef<HTMLDivElement>(null);

  // State
  const [pageData, setPageData] = useState(mockAIResponseData);
  const [messages, setMessages] = useState<ChatMessage[]>(mockAIResponseData.chatSession.messages);
  const [currentRating, setCurrentRating] = useState(0);
  const [isKBModalOpen, setIsKBModalOpen] = useState(false);
  const [attachedDocuments, setAttachedDocuments] = useState<Array<{ id: string; title: string }>>([]);
  const [isTyping, setIsTyping] = useState(false);

  // Scroll to bottom when messages change
  useEffect(() => {
    if (conversationRef.current) {
      conversationRef.current.scrollTop = conversationRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  // TODO: Load real data from backend based on emailId
  useEffect(() => {
    if (emailId) {
      console.log('Loading data for email:', emailId);
      // TODO: Replace with actual API call
      // fetchEmailData(emailId).then(data => setPageData(data));
    }
  }, [emailId]);

  const handleSendMessage = async (content: string, documentIds: string[]) => {
    // Add user message
    const userMessage: ChatMessage = {
      id: `msg-${Date.now()}`,
      sessionId: pageData.chatSession.id,
      content,
      sender: MessageSender.USER,
      timestamp: new Date(),
    };
    
    setMessages((prev) => [...prev, userMessage]);
    setAttachedDocuments([]);
    
    // Show typing indicator
    setIsTyping(true);

    // TODO: Replace with actual API call
    // const response = await sendMessageToBackend(content, documentIds);
    
    // Simulate API delay
    setTimeout(() => {
      const aiMessage: ChatMessage = {
        id: `msg-${Date.now()}`,
        sessionId: pageData.chatSession.id,
        content: generateMockAIResponse(content),
        sender: MessageSender.AI,
        timestamp: new Date(),
      };
      
      setMessages((prev) => [...prev, aiMessage]);
      setIsTyping(false);
    }, 1500);
  };

  const handleRegenerateDraft = async (modelId?: string) => {
    console.log('Regenerating draft with model:', modelId);
    
    // TODO: Replace with actual API call
    // const newDraft = await regenerateDraft(pageData.chatSession.id, modelId);
    // setPageData(prev => ({ ...prev, chatSession: { ...prev.chatSession, currentDraft: newDraft }}));
    
    // Simulate regeneration
    alert(`Draft regeneration requested with model: ${modelId}\n\nTODO: Implement backend API call`);
  };

  const handleAcceptDraft = () => {
    // TODO: Replace with actual API call
    // await acceptDraft(pageData.chatSession.currentDraft.id);
    
    // Store draft data in sessionStorage for email editor
    if (pageData.chatSession.currentDraft) {
      sessionStorage.setItem('acceptedResponse', pageData.chatSession.currentDraft.content);
      sessionStorage.setItem('ticketId', pageData.email.id);
      sessionStorage.setItem('customerName', pageData.customer.name);
      sessionStorage.setItem('customerEmail', pageData.customer.email);
      
      // Navigate to email editor
      navigate('/email-editor');
    }
  };

  const handleRateResponse = async (rating: number) => {
    setCurrentRating(rating);
    console.log('Rating submitted:', rating);
    
    // TODO: Replace with actual API call
    // await rateDraft(pageData.chatSession.currentDraft.id, rating);
  };

  const handleSelectDocument = (doc: KnowledgeDocument) => {
    if (!attachedDocuments.find(d => d.id === doc.id)) {
      setAttachedDocuments((prev) => [...prev, { id: doc.id, title: doc.title }]);
    }
  };

  const handleRemoveDocument = (docId: string) => {
    setAttachedDocuments((prev) => prev.filter(d => d.id !== docId));
  };

  return (
    <div className="ai-response-page">
      <TicketSidebar email={pageData.email} customer={pageData.customer} />

      <main className="main-content">
        <div className="conversation-area" ref={conversationRef}>
          <div className="page-header">
            <h1 className="page-title">AI-Generated Response</h1>
            <p className="page-subtitle">
              Review and approve the suggested response before sending to customer
            </p>
          </div>

          {/* Original customer message */}
          <MessageBubble
            message={messages[0]}
            customerName={pageData.customer.name}
          />

          {/* AI Response Box */}
          {pageData.chatSession.currentDraft && (
            <AIResponseBox
              draft={pageData.chatSession.currentDraft}
              availableModels={pageData.availableModels}
              onRegenerate={handleRegenerateDraft}
              onAccept={handleAcceptDraft}
              onRateResponse={handleRateResponse}
              currentRating={currentRating}
            />
          )}

          {/* Chat messages (follow-up conversation) */}
          {messages.slice(1).map((message) => (
            <MessageBubble
              key={message.id}
              message={message}
              customerName={pageData.customer.name}
            />
          ))}

          {/* Typing indicator */}
          {isTyping && (
            <div className="typing-indicator">
              <div className="typing-avatar">AI</div>
              <div className="typing-dots">
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
              </div>
            </div>
          )}
        </div>

        <ChatInput
          onSendMessage={handleSendMessage}
          onOpenKnowledgeBase={() => setIsKBModalOpen(true)}
          attachedDocuments={attachedDocuments}
          onRemoveDocument={handleRemoveDocument}
          disabled={isTyping}
        />
      </main>

      <KnowledgeBaseModal
        isOpen={isKBModalOpen}
        onClose={() => setIsKBModalOpen(false)}
        documents={mockKnowledgeDocuments}
        onSelectDocument={handleSelectDocument}
      />
    </div>
  );
};