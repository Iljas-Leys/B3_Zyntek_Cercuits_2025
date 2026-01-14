/* OLD EMAIL.TS FILE, keeping it in case of fix


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
  DRAFT = 'draft'
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
 */

// DB/API email ticket (matches your emails table exactly)
export type EmailDbCategory = 'BIOS' | 'Hardware' | 'Drivers';
export type EmailDbPriority = 'HIGH' | 'MEDIUM' | 'LOW' | 'URGENT';
export type EmailDbStatus = 'NEW' | 'REVIEWING' | 'APPROVED' | 'SENT';

export interface EmailDb {
  id: number;
  from_email: string;
  subject: string;
  body: string;

  received_at: string;
  resolved_at: string | null;

  category: EmailDbCategory;
  priority: EmailDbPriority;
  status: EmailDbStatus;

  assigned_to: number | null;
}
