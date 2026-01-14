// src/api/client.js

// If you already have env setup, you can replace this with an env var later.
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

/**
 * Simple fetch client that:
 * - prefixes API_BASE_URL
 * - sends JSON by default
 * - throws on non-2xx with helpful message
 * - returns parsed JSON (or null for 204)
 */
export default async function client(path, options = {}) {
    const url = path.startsWith('http') ? path : `${API_BASE_URL}${path}`;

    const headers = {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
    };

    const res = await fetch(url, {
        ...options,
        headers,
    });

    if (!res.ok) {
        const text = await res.text().catch(() => '');
        throw new Error(`HTTP ${res.status} ${res.statusText} - ${text}`);
    }

    // No content
    if (res.status === 204) return null;

    // Try JSON
    const contentType = res.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
        return await res.json();
    }

    // Fallback text
    return await res.text();
}
