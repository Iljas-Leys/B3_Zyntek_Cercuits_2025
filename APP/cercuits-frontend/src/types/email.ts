// Email types
export interface Email {
  id: string;
  from: string;
  to: string;
  cc?: string[];
  bcc?: string[];
  subject: string;
  body: string;
  htmlBody?: string;
  status: EmailStatus;
  priority: EmailPriority;
  category: EmailCategory;
  attachments?: Attachment[];
  createdAt: Date;
  updatedAt: Date;
  sentAt?: Date;
}

export enum EmailStatus {
  PENDING = 'pending',
  PROCESSED = 'processed',
  SENT = 'sent',
  FAILED = 'failed',
  DRAFT = 'draft',
  NEW = 'new',
  AWAITING_RESPONSE = 'awaiting_response'
}

export enum EmailPriority {
  LOW = 1,
  MEDIUM = 2,
  HIGH = 3,
  URGENT = 4
}

export enum EmailCategory {
  SUPPORT = 'support',
  SALES = 'sales',
  GENERAL = 'general',
  TECHNICAL = 'technical',
  BILLING = 'billing',
  OTHER = 'other'
}

export interface Attachment {
  id: string;
  name: string;
  size: number;
  type: string;
  url: string;
}

export interface EmailFilter {
  status?: EmailStatus;
  priority?: EmailPriority;
  category?: EmailCategory;
  dateFrom?: Date;
  dateTo?: Date;
  searchTerm?: string;
}

export interface EmailDraft {
  id?: string;
  to: string;
  cc?: string[];
  bcc?: string[];
  subject: string;
  body: string;
  attachments?: Attachment[];
  savedAt?: Date;
}
