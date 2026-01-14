import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './HomePage.module.css';

import { TicketSideNavFilter } from '../../components/tickets/TicketSideNavFilter/TicketSideNavFilter';
import { TicketsTable } from '../../components/tickets/TicketsTable/TicketsTable';
import { TicketSearchBar } from '../../components/layout/Search/TicketSearchBar/TicketSearchBar';

import { fetchEmails } from '../../api/emailApi';

// --- helpers ---
const toTitle = (s) => {
  if (!s) return '';
  const lower = String(s).toLowerCase();
  return lower.charAt(0).toUpperCase() + lower.slice(1);
};

const formatRelative = (iso) => {
  const time = new Date(iso).getTime();
  const diffMin = Math.floor((Date.now() - time) / 60000);

  if (diffMin < 1) return 'just now';
  if (diffMin < 60) return `${diffMin} min ago`;

  const h = Math.floor(diffMin / 60);
  if (h < 24) return `${h} hour${h === 1 ? '' : 's'} ago`;

  const d = Math.floor(h / 24);
  return `${d} day${d === 1 ? '' : 's'} ago`;
};

const formatDate = (iso) => {
  return new Date(iso).toLocaleString(undefined, {
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
};

const normalizeQuery = (q) => q.trim().toLowerCase();

const HomePage = () => {
  const navigate = useNavigate();

  // DB emails
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');

  // Filters (sidebar)
  const [selectedStatus, setSelectedStatus] = useState('All');
  const [selectedCategory, setSelectedCategory] = useState('All');

  // Search (top bar)
  const [ticketQuery, setTicketQuery] = useState('');

  const handleTicketClick = (ticketId) => {
    navigate(`/ai-response/${ticketId}`);
  };

  // 1) FETCH from backend
  useEffect(() => {
    let alive = true;

    (async () => {
      try {
        setLoading(true);
        setErrorMsg('');

        const data = await fetchEmails();
        if (!alive) return;

        setEmails(Array.isArray(data) ? data : []);
      } catch (e) {
        console.error(e);
        if (!alive) return;
        setErrorMsg(e?.message || 'Failed to load tickets.');
      } finally {
        if (!alive) return;
        setLoading(false);
      }
    })();

    return () => {
      alive = false;
    };
  }, []);

  // 2) MAP DB -> your table rows
  const tickets = useMemo(() => {
    return emails.map((e) => ({
      id: e.id,
      customer: e.from_email,
      category: e.category,
      priority: toTitle(e.priority),
      receivedLabel: formatRelative(e.received_at),
      receivedDate: formatDate(e.received_at),
      status: toTitle(e.status),
      title: e.subject, // search suggestions
    }));
  }, [emails]);

  const searchTickets = useMemo(() => {
    return tickets.map((t) => ({
      id: t.id,
      title: t.title,
      customer: t.customer,
    }));
  }, [tickets]);

  const filteredBySidebar = useMemo(() => {
    return tickets.filter((t) => {
      const statusOk =
        selectedStatus === 'All'
          ? true
          : selectedStatus === 'Urgent'
            ? t.priority === 'Urgent'
            : t.status === selectedStatus;

      const categoryOk = selectedCategory === 'All' ? true : t.category === selectedCategory;

      return statusOk && categoryOk;
    });
  }, [tickets, selectedStatus, selectedCategory]);

  const filteredTickets = useMemo(() => {
    const q = normalizeQuery(ticketQuery);
    if (!q) return filteredBySidebar;

    return filteredBySidebar.filter((t) => {
      const hay = `${t.id} ${t.title} ${t.customer} ${t.category} ${t.priority} ${t.status}`.toLowerCase();
      return hay.includes(q);
    });
  }, [filteredBySidebar, ticketQuery]);

  const handleTicketClick = (ticketId) => {
    navigate(`/ai-response/${ticketId}`);
  };

  return (
    <div className={styles.page}>
      <div className={styles.grid}>
        <TicketSideNavFilter
          tickets={tickets}
          selectedStatus={selectedStatus}
          selectedCategory={selectedCategory}
          onSelectStatus={setSelectedStatus}
          onSelectCategory={setSelectedCategory}
        />

        <div className={styles.main}>
          <div style={{ marginBottom: 12 }}>
            <TicketSearchBar
              tickets={searchTickets}
              onSearch={(q) => setTicketQuery(q)}
              placeholder="Search tickets by id, subject, customer…"
            />
          </div>

          {loading && <div style={{ padding: 16 }}>Loading tickets…</div>}
          {!loading && errorMsg && <div style={{ padding: 16, color: 'crimson' }}>{errorMsg}</div>}
          {!loading && !errorMsg && (
            <TicketsTable
              tickets={filteredTickets}
              onTicketClick={handleTicketClick}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default HomePage;