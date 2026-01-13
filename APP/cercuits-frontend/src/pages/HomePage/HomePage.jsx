import React, { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './HomePage.module.css';
import { TicketSearchBar } from '../../components/layout/Search/TicketSearchBar/TicketSearchBar';

const HomePage = () => {
  const navigate = useNavigate();

  // Mock tickets for now (replace later with API data)
  const [tickets] = useState([
    { id: 1024, title: "Customer can't upload Gerber files", customer: 'ACME' },
    { id: 1031, title: "Invoice mismatch (PO)", customer: 'NovaTech' },
    { id: 1042, title: "Delivery date change request", customer: 'Q-Boards' },
  ]);

  const [ticketQuery, setTicketQuery] = useState('');

  const filteredTickets = useMemo(() => {
    const q = ticketQuery.trim().toLowerCase();
    if (!q) return tickets;

    return tickets.filter((t) => {
      const hay = `${t.id} ${t.title} ${t.customer}`.toLowerCase();
      return hay.includes(q);
    });
  }, [tickets, ticketQuery]);

  const handleTicketClick = (ticketId) => {
    navigate(`/ai-response/${ticketId}`);
  };

  return (
    <div className={styles.homePage}>
      <h1 className={styles.title}>Welcome to Agent TSE</h1>
      <p className={styles.subtitle}>AI-powered email management system</p>

      {/* Ticket-only filter lives ONLY on HomePage */}
      <div className={styles.filterWrap}>
        <TicketSearchBar
          tickets={tickets}
          onSearch={(q) => setTicketQuery(q)}
          placeholder="Search tickets by id, title, customer…"
        />
      </div>

      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>Tickets</h2>

        {filteredTickets.length === 0 ? (
          <p className={styles.empty}>No tickets match your search.</p>
        ) : (
          <ul className={styles.ticketList}>
            {filteredTickets.map((t) => (
              <li key={t.id} className={styles.ticketItem}>
                <div className={styles.ticketId}>#{t.id}</div>
                <div className={styles.ticketTitle}>{t.title}</div>
                <div className={styles.ticketMeta}>{t.customer}</div>
                <button 
                  className={styles.ticketAction}
                  onClick={() => handleTicketClick(t.id)}
                  aria-label="View AI Response"
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="9 18 15 12 9 6"></polyline>
                  </svg>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default HomePage;