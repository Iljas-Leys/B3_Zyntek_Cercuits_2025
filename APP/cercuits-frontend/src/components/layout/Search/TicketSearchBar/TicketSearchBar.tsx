import React, { useEffect, useMemo, useRef, useState } from 'react';
import styles from './TicketSearchBar.module.css';

const DEFAULT_STORAGE_KEY = 'cercuits_recent_ticket_searches';

type Ticket = {
    id: number | string;
    title: string;
    customer?: string;
};

type Props = {
    placeholder?: string;
    tickets: Ticket[];
    onSearch?: (query: string) => void;
    recentStorageKey?: string;
    maxRecent?: number;
    minChars?: number;
};

type Item = {
    id: string;
    label: string;
};

export const TicketSearchBar: React.FC<Props> = ({
    placeholder = 'Search tickets…',
    tickets,
    onSearch,
    recentStorageKey = DEFAULT_STORAGE_KEY,
    maxRecent = 8,
    minChars = 2,
}) => {
    const [query, setQuery] = useState<string>('');
    const [open, setOpen] = useState<boolean>(false);
    const [activeIndex, setActiveIndex] = useState<number>(-1);
    const [recent, setRecent] = useState<string[]>([]);

    const containerRef = useRef<HTMLDivElement | null>(null);
    const inputRef = useRef<HTMLInputElement | null>(null);

    // Load recent searches
    useEffect(() => {
        try {
            const raw = localStorage.getItem(recentStorageKey);
            const parsed = raw ? (JSON.parse(raw) as unknown) : [];
            setRecent(Array.isArray(parsed) ? (parsed as string[]) : []);
        } catch {
            setRecent([]);
        }
    }, [recentStorageKey]);

    const persistRecent = (items: string[]) => {
        setRecent(items);
        localStorage.setItem(recentStorageKey, JSON.stringify(items));
    };

    const addRecent = (q: string) => {
        const trimmed = q.trim();
        if (!trimmed) return;

        const next = [trimmed, ...recent.filter((x) => x !== trimmed)].slice(0, maxRecent);
        persistRecent(next);
    };

    const clearRecent = () => persistRecent([]);

    // Close on outside click
    useEffect(() => {
        const onDocMouseDown = (e: MouseEvent) => {
            if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
                setOpen(false);
                setActiveIndex(-1);
            }
        };
        document.addEventListener('mousedown', onDocMouseDown);
        return () => document.removeEventListener('mousedown', onDocMouseDown);
    }, []);

    // Ticket-only suggestions
    const suggestions: Item[] = useMemo(() => {
        const q = query.trim().toLowerCase();
        if (q.length < minChars) return [];

        return tickets
            .filter((t) => {
                const hay = `${t.id ?? ''} ${t.title ?? ''} ${t.customer ?? ''}`.toLowerCase();
                return hay.includes(q);
            })
            .slice(0, 8)
            .map((t) => ({
                id: String(t.id),
                label: `#${t.id} — ${t.title}`,
            }));
    }, [query, tickets, minChars]);

    const showRecents = query.trim().length === 0;

    const items: Item[] = useMemo(() => {
        return showRecents
            ? recent.map((r) => ({ id: `recent:${r}`, label: r }))
            : suggestions;
    }, [showRecents, recent, suggestions]);

    const submit = (q: string) => {
        const trimmed = q.trim();
        if (!trimmed) return;

        addRecent(trimmed);
        onSearch?.(trimmed);

        setOpen(false);
        setActiveIndex(-1);
        inputRef.current?.blur(); // ✅ now works because inputRef is typed
    };

    const clearQuery = () => {
        setQuery('');
        setActiveIndex(-1);
        setOpen(true);
        inputRef.current?.focus();
    };

    const onKeyDown: React.KeyboardEventHandler<HTMLInputElement> = (e) => {
        if (!open && (e.key === 'ArrowDown' || e.key === 'ArrowUp')) {
            setOpen(true);
            return;
        }

        if (e.key === 'Escape') {
            setOpen(false);
            setActiveIndex(-1);
            return;
        }

        if (e.key === 'Enter') {
            if (open && activeIndex >= 0 && activeIndex < items.length) {
                submit(items[activeIndex].label);
            } else {
                submit(query);
            }
            return;
        }

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (!items.length) return;
            setActiveIndex((idx) => (idx + 1) % items.length);
            return;
        }

        if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (!items.length) return;
            setActiveIndex((idx) => (idx - 1 + items.length) % items.length);
        }
    };

    return (
        <div className={styles.searchbar} ref={containerRef}>
            <div className={`${styles.inputWrap} ${open ? styles.open : ''}`}>
                <span className={styles.icon} aria-hidden="true">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <circle cx="11" cy="11" r="7"></circle>
                        <path d="M21 21l-4.3-4.3"></path>
                    </svg>
                </span>

                <input
                    ref={inputRef}
                    className={styles.input}
                    value={query}
                    placeholder={placeholder}
                    onChange={(e) => {
                        setQuery(e.target.value);
                        setOpen(true);
                        setActiveIndex(-1);
                    }}
                    onFocus={() => setOpen(true)}
                    onKeyDown={onKeyDown}
                />

                {query.trim().length > 0 && (
                    <button className={styles.clearBtn} type="button" onClick={clearQuery} aria-label="Clear search">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M18 6L6 18"></path>
                            <path d="M6 6l12 12"></path>
                        </svg>
                    </button>
                )}
            </div>

            {open && (
                <div className={styles.dropdown}>
                    <div className={styles.dropdownHeader}>
                        <span className={styles.dropdownTitle}>
                            {showRecents ? 'Recent ticket searches' : 'Ticket suggestions'}
                        </span>

                        {showRecents && recent.length > 0 && (
                            <button className={styles.clearRecent} type="button" onClick={clearRecent}>
                                Clear
                            </button>
                        )}
                    </div>

                    {items.length === 0 ? (
                        <div className={styles.empty}>
                            {showRecents ? 'No recent searches yet.' : 'No ticket matches.'}
                        </div>
                    ) : (
                        <ul className={styles.list}>
                            {items.map((item, idx) => (
                                <li key={item.id}>
                                    <button
                                        type="button"
                                        className={`${styles.item} ${idx === activeIndex ? styles.active : ''}`}
                                        onMouseEnter={() => setActiveIndex(idx)}
                                        onMouseDown={(e) => e.preventDefault()}
                                        onClick={() => submit(item.label)}
                                    >
                                        {item.label}
                                    </button>
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
            )}
        </div>
    );
};
