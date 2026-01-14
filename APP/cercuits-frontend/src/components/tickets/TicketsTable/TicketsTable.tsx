import React from 'react';
import styles from './TicketsTable.module.css';
import type { Ticket } from '../TicketSideNavFilter/TicketSideNavFilter';

type Props = {
    tickets: Ticket[];
};

export const TicketsTable: React.FC<Props> = ({ tickets }) => {
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
                                <button className={styles.actionBtn} type="button" aria-label="Open ticket">
                                    ›
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
