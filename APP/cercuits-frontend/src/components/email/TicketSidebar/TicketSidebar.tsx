import React from 'react';
import { Email, EmailPriority, EmailStatus } from '../../../types/email';
import { CustomerInfo } from '../../../types/aiResponse';
import './TicketSidebar.css';

interface TicketSidebarProps {
  email: Email;
  customer: CustomerInfo;
}

export const TicketSidebar: React.FC<TicketSidebarProps> = ({ email, customer }) => {
  const getPriorityClass = (priority: EmailPriority) => {
    switch (priority) {
      case EmailPriority.URGENT:
        return 'priority-urgent';
      case EmailPriority.HIGH:
        return 'priority-high';
      case EmailPriority.MEDIUM:
        return 'priority-medium';
      case EmailPriority.LOW:
        return 'priority-low';
      default:
        return 'priority-medium';
    }
  };

  const getStatusClass = (status: EmailStatus) => {
    switch (status) {
      case EmailStatus.NEW:
        return 'status-new';
      case EmailStatus.PROCESSED:
        return 'status-processed';
      case EmailStatus.AWAITING_RESPONSE:
        return 'status-awaiting-response';
      case EmailStatus.SENT:
        return 'status-sent';
      default:
        return 'status-new';
    }
  };

  const formatTimeAgo = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 1) return 'just now';
    if (minutes < 60) return `${minutes} min ago`;
    
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    
    const days = Math.floor(hours / 24);
    return `${days} day${days > 1 ? 's' : ''} ago`;
  };

  const getCustomerInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .substring(0, 2);
  };

  return (
    <aside className="ticket-sidebar">
      <div className="ticket-info">
        <div className="ticket-id">{email.id}</div>
        <div className="ticket-title">{email.subject}</div>

        <div className="info-row">
          <span className="info-label">Priority:</span>
          <span className={`priority-badge ${getPriorityClass(email.priority)}`}>
            <span className="priority-dot"></span>
            {email.priority}
          </span>
        </div>

        <div className="info-row">
          <span className="info-label">Status:</span>
          <span className={`status-badge ${getStatusClass(email.status)}`}>
            {email.status}
          </span>
        </div>

        <div className="info-row">
          <span className="info-label">Received:</span>
          <span>{formatTimeAgo(email.createdAt)}</span>
        </div>

        <div className="info-row">
          <span className="info-label">Category:</span>
          <span>{email.category}</span>
        </div>
      </div>

      <div className="sidebar-divider"></div>

      <div className="customer-section">
        <div className="customer-info-title">Customer Information</div>
        <div className="customer-card">
          <div className="customer-avatar">
            {customer.avatar ? (
              <img src={customer.avatar} alt={customer.name} />
            ) : (
              getCustomerInitials(customer.name)
            )}
          </div>
          <div className="customer-details">
            <div className="customer-name">{customer.name}</div>
            {customer.company && (
              <div className="customer-company">{customer.company}</div>
            )}
            <div className="customer-email">{customer.email}</div>
          </div>
        </div>
      </div>
    </aside>
  );
};