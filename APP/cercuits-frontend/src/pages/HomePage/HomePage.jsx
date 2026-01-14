/* 
OLD HOMEPAGE CONTENT:

import React from 'react';
import './HomePage.module.css';

const HomePage = () => {
  return (
    <div className="home-page">
      <h1>Welcome to Agent TSE</h1>
      <p>AI-powered email management system</p>
    </div>
  );
};

export default HomePage; */


/* Before map + fetch

import React, { useMemo, useState } from 'react';
import styles from './HomePage.module.css';

import { TicketSideNavFilter } from '../../components/tickets/TicketSideNavFilter/TicketSideNavFilter';
import { TicketsTable } from '../../components/tickets/TicketsTable/TicketsTable';

const HomePage = () => {
  // Mock ticket data (replace later with API/DB)
  const [tickets] = useState([
    {
      id: '#GM-01231',
      customer: 'Gabriel Manifesto',
      category: 'BIOS configuration',
      priority: 'High',
      receivedLabel: '5 min ago',
      receivedDate: 'Nov 17, 10:42 AM',
      status: 'New',
    },
    {
      id: '#GM-01232',
      customer: 'Gabriel Manifesto',
      category: 'Hardware failure',
      priority: 'Medium',
      receivedLabel: '1 hour ago',
      receivedDate: 'Nov 17, 9:42 AM',
      status: 'New',
    },
    {
      id: '#GM-01233',
      customer: 'Gabriel Manifesto',
      category: 'Hardware failure',
      priority: 'Low',
      receivedLabel: '5 hours ago',
      receivedDate: 'Nov 17, 5:42 AM',
      status: 'Waiting',
    },
    {
      id: '#GM-01234',
      customer: 'Gabriel Manifesto',
      category: 'BIOS configuration',
      priority: 'Medium',
      receivedLabel: '1 day ago',
      receivedDate: 'Nov 16, 10:42 AM',
      status: 'In Progress',
    },
    {
      id: '#GM-01235',
      customer: 'Gabriel Manifesto',
      category: 'Driver issue',
      priority: 'Urgent',
      receivedLabel: '1 day ago',
      receivedDate: 'Nov 16, 9:42 AM',
      status: 'In Progress',
    },
    {
      id: '#GM-01236',
      customer: 'Gabriel Manifesto',
      category: 'Power issue',
      priority: 'Medium',
      receivedLabel: '1 day ago',
      receivedDate: 'Nov 16, 7:42 AM',
      status: 'Resolved',
    },
    {
      id: '#GM-01237',
      customer: 'Gabriel Manifesto',
      category: 'Chipset drivers',
      priority: 'Medium',
      receivedLabel: '1 week ago',
      receivedDate: 'Nov 10, 5:07 AM',
      status: 'Archived',
    },
  ]);

  // Filters
  const [selectedStatus, setSelectedStatus] = useState('All');
  const [selectedCategory, setSelectedCategory] = useState('All');

  const filteredTickets = useMemo(() => {
    return tickets.filter((t) => {
      // Special "Urgent" entry filters by PRIORITY, not status (matches your sidebar idea)
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
          <TicketsTable tickets={filteredTickets} />
        </div>
      </div>
    </div>
  );
};

export default HomePage; */

import React, { useEffect, useMemo, useState } from 'react';
import styles from './HomePage.module.css';

import { TicketSideNavFilter } from '../../components/tickets/TicketSideNavFilter/TicketSideNavFilter';
import { TicketsTable } from '../../components/tickets/TicketsTable/TicketsTable';

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

const HomePage = () => {
  // DB emails
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');

  // Filters
  const [selectedStatus, setSelectedStatus] = useState('All');
  const [selectedCategory, setSelectedCategory] = useState('All');

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
      priority: toTitle(e.priority), // "high" -> "High"
      receivedLabel: formatRelative(e.received_at),
      receivedDate: formatDate(e.received_at),
      status: toTitle(e.status), // "new" -> "New"
    }));
  }, [emails]);

  // 3) Apply filters
  const filteredTickets = useMemo(() => {
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
          {loading && <div style={{ padding: 16 }}>Loading tickets…</div>}
          {!loading && errorMsg && <div style={{ padding: 16, color: 'crimson' }}>{errorMsg}</div>}
          {!loading && !errorMsg && <TicketsTable tickets={filteredTickets} />}
        </div>
      </div>
    </div>
  );
};

export default HomePage;
