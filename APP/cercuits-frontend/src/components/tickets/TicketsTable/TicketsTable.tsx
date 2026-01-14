import React from 'react';
import styles from './TicketsTable.module.css';
import type { Ticket } from '../TicketSideNavFilter/TicketSideNavFilter';

type Props = {
    tickets: Ticket[];
    onTicketClick?: (ticketId: number) => void;
};

export const TicketsTable: React.FC<Props> = ({ tickets, onTicketClick }) => {
    return (
        <div className={styles.wrap}>
            <table className={styles.table}>
                <thead>
                    <tr>
                        <th>INQUIRY ID</th>
                        <th>CUSTOMER</th>
                        <th>CATEGORY</th>
                        <th>PRIORITY</th>
                        <th>RECEIVED</th>
                        <th>STATUS</th>
                        <th>ACTIONS</th>
                    </tr>
                </thead>

                <tbody>
                    {tickets.map((t) => (
                        <tr key={t.id}>
                            <td className={styles.link}>{t.id}</td>
                            <td>{t.customer}</td>
                            <td>
                                <span className={styles.pillGrey}>{t.category}</span>
                            </td>
                            <td>
                                <span className={`${styles.priority} ${styles['p_' + t.priority.replace(' ', '')]}`}>
                                    <span className={styles.dot} />
                                    {t.priority}
                                </span>
                            </td>
                            <td>
                                <div className={styles.receivedTop}>{t.receivedLabel}</div>
                                <div className={styles.receivedBottom}>{t.receivedDate}</div>
                            </td>
                            <td>
                                <span className={`${styles.status} ${styles['s_' + t.status.replace(' ', '')]}`}>
                                    {t.status}
                                </span>
                            </td>
                            <td>
                                <button
                                    className={styles.actionBtn}
                                    type="button"
                                    aria-label="View AI Response"
                                    onClick={() => onTicketClick?.(t.id)}
                                >
                                    <svg
                                        width="18"
                                        height="18"
                                        viewBox="0 0 24 24"
                                        fill="none"
                                        stroke="currentColor"
                                        strokeWidth="2"
                                        aria-hidden="true"
                                        focusable="false"
                                    >
                                        <polyline points="9 18 15 12 9 6"></polyline>
                                    </svg>
                                </button>
                            </td>
                        </tr>
                    ))}

                    {tickets.length === 0 && (
                        <tr>
                            <td colSpan={7} className={styles.empty}>
                                No tickets match your filters.
                            </td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );
};
