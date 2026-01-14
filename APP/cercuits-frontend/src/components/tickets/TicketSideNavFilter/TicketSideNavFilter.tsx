import React from 'react';
import styles from './TicketSideNavFilter.module.css';

// ✅ Matches what HomePage now passes (DB-mapped tickets)
export type TicketStatus =
    | 'New'
    | 'Reviewing'
    | 'Approved'
    | 'Sent'
    | 'Resolved'
    | 'Archived';

export type TicketPriority = 'Urgent' | 'High' | 'Medium' | 'Low';

export type Ticket = {
    id: number;            // DB id
    customer: string;      // from_email
    category: string;      // "BIOS" | "Drivers" | ...
    priority: TicketPriority;
    status: TicketStatus;
    receivedLabel: string;
    receivedDate: string;

    // optional: used by TicketSearchBar mapping
    title?: string;        // subject
};

type StatusFilter = TicketStatus | 'All' | 'Urgent';

type Props = {
    tickets: Ticket[];
    selectedStatus: StatusFilter;
    selectedCategory: string | 'All';
    onSelectStatus: (status: StatusFilter) => void;
    onSelectCategory: (category: string | 'All') => void;
};

export const TicketSideNavFilter: React.FC<Props> = ({
    tickets,
    selectedStatus,
    selectedCategory,
    onSelectStatus,
    onSelectCategory,
}) => {
    const countAll = tickets.length;

    // "Urgent" is a special shortcut based on priority
    const countUrgent = tickets.filter((t) => t.priority === 'Urgent').length;

    const countByStatus = (status: TicketStatus) =>
        tickets.filter((t) => t.status === status).length;

    // Only show status entries that actually exist in current data,
    // but keep a consistent preferred order.
    const preferredStatusOrder: TicketStatus[] = [
        'New',
        'Reviewing',
        'Approved',
        'Sent',
        'Resolved',
        'Archived',
    ];

    const statusesToShow = preferredStatusOrder.filter(
        (s) => countByStatus(s) > 0
    );

    const categoryCounts = tickets.reduce<Record<string, number>>((acc, t) => {
        acc[t.category] = (acc[t.category] ?? 0) + 1;
        return acc;
    }, {});

    const categoriesSorted = Object.entries(categoryCounts)
        .sort((a, b) => b[1] - a[1])
        .map(([name]) => name);

    return (
        <aside className={styles.sidebar}>
            <div className={styles.group}>
                <button
                    type="button"
                    className={`${styles.item} ${selectedStatus === 'All' ? styles.active : ''}`}
                    onClick={() => onSelectStatus('All')}
                >
                    <span className={styles.label}>All Inquiries</span>
                    <span className={styles.count}>{countAll}</span>
                </button>

                <button
                    type="button"
                    className={`${styles.item} ${selectedStatus === 'Urgent' ? styles.active : ''}`}
                    onClick={() => onSelectStatus('Urgent')}
                >
                    <span className={styles.label}>Urgent</span>
                    <span className={styles.count}>{countUrgent}</span>
                </button>

                {statusesToShow.map((status) => (
                    <button
                        key={status}
                        type="button"
                        className={`${styles.item} ${selectedStatus === status ? styles.active : ''}`}
                        onClick={() => onSelectStatus(status)}
                    >
                        <span className={styles.label}>{status}</span>
                        <span className={styles.count}>{countByStatus(status)}</span>
                    </button>
                ))}
            </div>

            <div className={styles.divider} />

            <div className={styles.group}>
                <div className={styles.groupTitleRow}>
                    <div className={styles.groupTitle}>Categories</div>
                    <button
                        type="button"
                        className={styles.reset}
                        onClick={() => onSelectCategory('All')}
                    >
                        Reset
                    </button>
                </div>

                <button
                    type="button"
                    className={`${styles.item} ${selectedCategory === 'All' ? styles.active : ''}`}
                    onClick={() => onSelectCategory('All')}
                >
                    <span className={styles.label}>All Categories</span>
                    <span className={styles.count}>{countAll}</span>
                </button>

                {categoriesSorted.map((cat) => (
                    <button
                        key={cat}
                        type="button"
                        className={`${styles.item} ${selectedCategory === cat ? styles.active : ''}`}
                        onClick={() => onSelectCategory(cat)}
                    >
                        <span className={styles.label}>{cat}</span>
                        <span className={styles.count}>{categoryCounts[cat]}</span>
                    </button>
                ))}
            </div>
        </aside>
    );
};
