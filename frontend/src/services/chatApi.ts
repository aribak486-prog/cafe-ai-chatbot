import type { Message } from '../types/chat';
const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api';
async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, { headers: { 'Content-Type': 'application/json' }, ...options });
  if (!response.ok) { const body = await response.json().catch(() => ({})); throw new Error(body.detail ?? 'Something went wrong. Please try again.'); }
  return response.status === 204 ? undefined as T : response.json();
}
export const createConversation = () => request<{conversation_id:string}>('/conversations', { method: 'POST' });
export const sendMessage = (conversation_id: string, message: string) => request<{conversation_id:string; response:string}>('/chat', { method: 'POST', body: JSON.stringify({ conversation_id, message }) });
export const getConversation = (id: string) => request<{conversation_id:string;messages:Message[]}>(`/conversations/${id}`);
export const deleteConversation = (id: string) => request<void>(`/conversations/${id}`, {method:'DELETE'});
