// Knowledge base types
export interface Document {
  id: string;
  name: string;
  description?: string;
  content: string;
  type: DocumentType;
  size: number;
  status: DocumentStatus;
  metadata?: DocumentMetadata;
  uploadedBy: string;
  createdAt: Date;
  updatedAt: Date;
  lastIndexedAt?: Date;
}

export enum DocumentType {
  PDF = 'pdf',
  WORD = 'word',
  TEXT = 'text',
  HTML = 'html',
  MARKDOWN = 'markdown'
}

export enum DocumentStatus {
  UPLOADING = 'uploading',
  PROCESSING = 'processing',
  INDEXED = 'indexed',
  FAILED = 'failed',
  ARCHIVED = 'archived'
}

export interface DocumentMetadata {
  author?: string;
  title?: string;
  tags?: string[];
  category?: string;
  language?: string;
  pageCount?: number;
  wordCount?: number;
}

export interface DocumentUploadRequest {
  file: File;
  metadata?: Partial<DocumentMetadata>;
}

export interface DocumentSearchRequest {
  query: string;
  filters?: DocumentFilter;
  limit?: number;
}

export interface DocumentFilter {
  type?: DocumentType;
  status?: DocumentStatus;
  category?: string;
  tags?: string[];
  dateFrom?: Date;
  dateTo?: Date;
}

export interface DocumentSearchResult {
  document: Document;
  relevanceScore: number;
  highlights?: string[];
}

export interface EmbeddingModel {
  id: string;
  name: string;
  version: string;
  status: ModelStatus;
  dimensions: number;
  createdAt: Date;
  lastUsedAt?: Date;
}

export enum ModelStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  TRAINING = 'training',
  LOADING = 'loading',
  ERROR = 'error'
}

export interface KnowledgeBaseStats {
  totalDocuments: number;
  indexedDocuments: number;
  totalSize: number;
  lastUpdated: Date;
  modelInfo?: EmbeddingModel;
}
