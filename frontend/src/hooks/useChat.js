import { useState, useCallback, useRef } from 'react';
import { sendMessage } from '../utils/api';

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const conversationIdRef = useRef(null);

  const addMessage = useCallback((msg) => {
    setMessages(prev => [...prev, msg]);
  }, []);

  const ask = useCallback(async (question) => {
    if (!question.trim() || isLoading) return;

    addMessage({
      id: Date.now(),
      role: 'user',
      content: question.trim(),
      timestamp: new Date().toISOString(),
    });

    setIsLoading(true);
    setError(null);

    try {
      const result = await sendMessage(question.trim(), conversationIdRef.current);
      conversationIdRef.current = result.conversation_id;

      addMessage({
        id: Date.now() + 1,
        role: 'assistant',
        content: result.answer,
        sources: result.sources || [],
        evidence_status: result.evidence_status,
        abstained: result.abstained,
        timestamp: new Date().toISOString(),
      });
    } catch (err) {
      setError(err.message);
      addMessage({
        id: Date.now() + 1,
        role: 'assistant',
        content: `Connection error: ${err.message}. Please check if the backend server is running on port 8000.`,
        sources: [],
        evidence_status: 'error',
        abstained: false,
        timestamp: new Date().toISOString(),
      });
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, addMessage]);

  const clearChat = useCallback(() => {
    setMessages([]);
    conversationIdRef.current = null;
    setError(null);
  }, []);

  return { messages, isLoading, error, ask, clearChat };
}
