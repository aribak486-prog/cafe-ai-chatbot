export type Role = 'user' | 'assistant';
export interface Message { role: Role; content: string; }
export interface Conversation { id: string; messages: Message[]; }
