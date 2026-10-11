import { useAction } from 'convex/react';
export function useChat() { return useAction('chat:ask'); }
