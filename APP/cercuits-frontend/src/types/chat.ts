// Chat and AI response types
export interface ChatMessage {
  id: string;
  sessionId: string;
  content: string;
  sender: MessageSender;
  timestamp: Date;
  metadata?: MessageMetadata;
}

export enum MessageSender {
  USER = 'user',
  AI = 'ai',
  SYSTEM = 'system'
}

export interface MessageMetadata {
  tokens?: number;
  model?: string;
  processingTime?: number;
  confidence?: number;
}

export interface ChatSession {
  id: string;
  userId: string;
  emailId?: string;
  messages: ChatMessage[];
  status: SessionStatus;
  createdAt: Date;
  updatedAt: Date;
}

export enum SessionStatus {
  ACTIVE = 'active',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled'
}

export interface DraftResponse {
  id: string;
  emailId: string;
  sessionId: string;
  content: string;
  sourceDocuments?: SourceDocument[];
  confidence: number;
  createdAt: Date;
  version: number;
}

export interface SourceDocument {
  id: string;
  name: string;
  excerpt: string;
  relevanceScore: number;
  pageNumber?: number;
}

export interface RegenerationRequest {
  draftId: string;
  feedback?: string;
  parameters?: {
    tone?: string;
    length?: string;
    style?: string;
  };
}

export interface ChatResponse {
  message: ChatMessage;
  draft?: DraftResponse;
  suggestions?: string[];
}
