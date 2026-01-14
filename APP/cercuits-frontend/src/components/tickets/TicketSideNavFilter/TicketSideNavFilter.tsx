import React from 'react';
import styles from './TicketSideNavFilter.module.css';

export type TicketStatus = 'New' | 'Waiting' | 'In Progress' | 'Resolved' | 'Archived';
export type TicketPriority = 'Urgent' | 'High' | 'Medium' | 'Low';

export type Ticket = {
    id: string;           // #GM-01231
    customer: string;     // Gabriel Manifesto
    category: string;     // BIOS configuration
    priority: TicketPriority;
    status: TicketStatus;
    receivedLabel: string; // "5 min ago"
    receivedDate: string;  // "Nov 17, 10:42 AM"
};

type Props = {
    tickets: Ticket[];
    selectedStatus: TicketStatus | 'All';
    selectedCategory: string | 'All';
    onSelectStatus: (status: TicketStatus | 'All') => void;
    onSelectCategory: (category: string | 'All') => void;
};

export const TicketSideNavFilter: React.FC<Props> = ({
    tickets,
    selectedStatus,
    selectedCategory,
    onSelectStatus,
    onSelectCategory,
}) => {
    const statusOrder: (TicketStatus | 'All')[] = ['All', 'Urgent' as any, 'In Progress', 'Resolved', 'Archived'];
    // We'll render "Urgent" as a special shortcut based on priority, like the UI in your screenshot.
    // Statuses stay real statuses; urgent is a special entry.

    const countAll = tickets.length;

    const countUrgent = tickets.filter(t => t.priority === 'Urgent').length;

    const countByStatus = (status: TicketStatus) =>
        tickets.filter((t) => t.status === status).length;

    const categoryCounts = tickets.reduce<Record<string, number>>((acc, t) => {
        acc[t.category] = (acc[t.category] ?? 0) + 1;
        return acc;
    }, {});

    const categoriesSorted = Object.entries(categoryCounts)
        .sort((a, b) => b[1] - a[1])
        .map(([name]) => name);

    const isUrgentSelected = selectedStatus === ('Urgent' as any);

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
                    className={`${styles.item} ${isUrgentSelected ? styles.active : ''}`}
                    onClick={() => onSelectStatus('Urgent' as any)}
                >
                    <span className={styles.label}>Urgent</span>
                    <span className={styles.count}>{countUrgent}</span>
                </button>

                <button
                    type="button"
                    className={`${styles.item} ${selectedStatus === 'In Progress' ? styles.active : ''}`}
                    onClick={() => onSelectStatus('In Progress')}
                >
                    <span className={styles.label}>In Progress</span>
                    <span className={styles.count}>{countByStatus('In Progress')}</span>
                </button>

                <button
                    type="button"
                    className={`${styles.item} ${selectedStatus === 'Resolved' ? styles.active : ''}`}
                    onClick={() => onSelectStatus('Resolved')}
                >
                    <span className={styles.label}>Resolved</span>
                    <span className={styles.count}>{countByStatus('Resolved')}</span>
                </button>

                <button
                    type="button"
                    className={`${styles.item} ${selectedStatus === 'Archived' ? styles.active : ''}`}
                    onClick={() => onSelectStatus('Archived')}
                >
                    <span className={styles.label}>Archived</span>
                    <span className={styles.count}>{countByStatus('Archived')}</span>
                </button>
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
