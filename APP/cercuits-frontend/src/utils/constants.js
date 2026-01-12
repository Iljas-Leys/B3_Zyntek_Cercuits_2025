// API Configuration
export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// Email Status
export const EMAIL_STATUS = {
  PENDING: 'pending',
  PROCESSED: 'processed',
  SENT: 'sent',
  FAILED: 'failed',
  DRAFT: 'draft'
};

// Email Priority
export const EMAIL_PRIORITY = {
  LOW: 1,
  MEDIUM: 2,
  HIGH: 3,
  URGENT: 4
};

// Email Categories
export const EMAIL_CATEGORIES = {
  SUPPORT: 'support',
  SALES: 'sales',
  GENERAL: 'general',
  TECHNICAL: 'technical',
  BILLING: 'billing',
  OTHER: 'other'
};

// System Health Status
export const HEALTH_STATUS = {
  HEALTHY: 'healthy',
  WARNING: 'warning',
  ERROR: 'error',
  UNKNOWN: 'unknown'
};

// Notification Types
export const NOTIFICATION_TYPES = {
  INFO: 'info',
  SUCCESS: 'success',
  WARNING: 'warning',
  ERROR: 'error'
};

// Date Formats
export const DATE_FORMATS = {
  SHORT: 'MM/DD/YYYY',
  LONG: 'MMMM DD, YYYY',
  TIME: 'HH:mm:ss',
  DATETIME: 'MM/DD/YYYY HH:mm:ss'
};

// Pagination
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  PAGE_SIZE_OPTIONS: [10, 20, 50, 100]
};

// File Upload
export const FILE_UPLOAD = {
  MAX_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_TYPES: [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain'
  ]
};

// Routes
export const ROUTES = {
  HOME: '/',
  AI_RESPONSE: '/ai-response',
  EMAIL_EDITOR: '/email-editor',
  KNOWLEDGE_BASE: '/knowledge-base',
  MONITORING: '/monitoring',
  CONSISTENCY_TEST: '/consistency-test'
};
