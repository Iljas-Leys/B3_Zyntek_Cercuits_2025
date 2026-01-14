// src/api/emailApi.js
import client from './client';

export const fetchEmails = async () => {
    return await client('/api/emails');
};

export const fetchEmailById = async (id) => {
    return await client(`/api/emails/${id}`);
};

export const patchEmail = async (id, payload) => {
    return await client(`/api/emails/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(payload),
    });
};
