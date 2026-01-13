// AI Response specific types extending base chat types
import { ChatMessage, DraftResponse, SourceDocument } from './chat';
import { Email } from './email';
import { User } from './user';

export interface AIResponsePageData {
  email: Email;
  customer: CustomerInfo;
  chatSession: AIResponseSession;
  availableModels: AIModel[];
}

export interface CustomerInfo {
  id: string;
  name: string;
  email: string;
  company?: string;
  avatar?: string;
}

export interface AIResponseSession {
  id: string;
  emailId: string;
  messages: ChatMessage[];
  currentDraft?: DraftResponse;
  status: 'active' | 'completed';
  rating?: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface AIModel {
  id: string;
  name: string;
  displayName: string;
  description?: string;
  isActive: boolean;
}

export interface RegenerateDraftRequest {
  sessionId: string;
  feedback?: string;
  useModel?: string;
}

export interface SendMessageRequest {
  sessionId: string;
  content: string;
  attachedDocuments?: string[]; // document IDs
}

export interface RateDraftRequest {
  draftId: string;
  rating: number; // 1-5
}

export interface AcceptDraftRequest {
  draftId: string;
  sessionId: string;
}

// For Knowledge Base Modal
export interface KnowledgeDocument {
  id: string;
  title: string;
  fileName: string;
  fileType: 'pdf' | 'docx' | 'txt' | 'xlsx';
  fileSize: string;
  category?: string;
}