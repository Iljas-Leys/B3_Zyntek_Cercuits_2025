// Date and time formatters
export const formatDate = (date) => {
  if (!date) return '';
  const d = new Date(date);
  return d.toLocaleDateString();
};

export const formatDateTime = (date) => {
  if (!date) return '';
  const d = new Date(date);
  return d.toLocaleString();
};

export const formatTime = (date) => {
  if (!date) return '';
  const d = new Date(date);
  return d.toLocaleTimeString();
};

// Status formatters
export const formatStatus = (status) => {
  if (!status) return 'Unknown';
  return status.charAt(0).toUpperCase() + status.slice(1).toLowerCase();
};

// Email category formatters
export const formatCategory = (category) => {
  if (!category) return 'Uncategorized';
  return category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

// Priority formatters
export const formatPriority = (priority) => {
  const priorities = {
    1: 'Low',
    2: 'Medium',
    3: 'High',
    4: 'Urgent'
  };
  return priorities[priority] || 'Normal';
};

// Number formatters
export const formatNumber = (num) => {
  if (!num) return '0';
  return num.toLocaleString();
};

export const formatPercentage = (value, decimals = 1) => {
  if (!value) return '0%';
  return `${value.toFixed(decimals)}%`;
};

// File size formatter
export const formatFileSize = (bytes) => {
  if (!bytes) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
};
