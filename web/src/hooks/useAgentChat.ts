import { useCallback, useEffect, useRef, useState } from 'react';
import { toast } from 'react-toastify';

import { useAppDispatch, useAppSelector } from '@/store';
import { baseApi } from '@/api/baseApi';
import { MessageRole, type Message } from '@/types/chat';
import type {
  UseAgentChatOptions,
  UseAgentChatReturn,
} from '@/types/agentChat';
import { AgentChatSocket } from '@/services/agentChatSocket';

export const useAgentChat = ({
  agentId,
  initialConversationId,
  initialMessages,
}: UseAgentChatOptions): UseAgentChatReturn => {
  const token = useAppSelector(state => state.auth.token);
  const dispatch = useAppDispatch();

  const [messages, setMessages] = useState<Message[]>(initialMessages ?? []);
  const [streamingContent, setStreamingContent] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(
    initialConversationId ?? null,
  );

  const socketRef = useRef<AgentChatSocket | null>(null);
  const conversationIdRef = useRef<string | null>(
    initialConversationId ?? null,
  );
  const streamingBufferRef = useRef('');
  const seededRef = useRef(false);

  // Reset all state when the conversation or agent changes
  useEffect(() => {
    seededRef.current = false;
    setMessages([]);
    setStreamingContent('');
    setIsStreaming(false);
    streamingBufferRef.current = '';
    conversationIdRef.current = initialConversationId ?? null;
    setConversationId(initialConversationId ?? null);
  }, [agentId, initialConversationId]);

  // Seed messages once the async query resolves
  useEffect(() => {
    if (initialMessages && !seededRef.current) {
      seededRef.current = true;
      setMessages(initialMessages);
    }
  }, [initialMessages]);

  useEffect(() => {
    if (!token || !agentId) return;

    const socket = new AgentChatSocket(agentId, token, {
      onToken: token => {
        streamingBufferRef.current += token;
        setStreamingContent(streamingBufferRef.current);
      },
      onDone: ({ conversation_id }) => {
        const content = streamingBufferRef.current;
        streamingBufferRef.current = '';
        const isNewConversation = !conversationIdRef.current;
        conversationIdRef.current = conversation_id;
        setConversationId(conversation_id);
        dispatch(
          baseApi.util.invalidateTags([{ type: 'PlatformLLM', id: 'LIST' }]),
        );
        if (isNewConversation) {
          dispatch(
            baseApi.util.invalidateTags([{ type: 'Conversation', id: 'LIST' }]),
          );
        }
        setStreamingContent('');
        if (content) {
          setMessages(msgs => [
            ...msgs,
            { id: Date.now().toString(), role: MessageRole.Assistant, content },
          ]);
        }
        setIsStreaming(false);
      },
      onStopped: ({ conversation_id }) => {
        const content = streamingBufferRef.current;
        streamingBufferRef.current = '';
        conversationIdRef.current = conversation_id;
        setConversationId(conversation_id);
        setStreamingContent('');
        if (content) {
          setMessages(msgs => [
            ...msgs,
            { id: Date.now().toString(), role: MessageRole.Assistant, content },
          ]);
        }
        setIsStreaming(false);
      },
      onError: message => {
        streamingBufferRef.current = '';
        setStreamingContent('');
        setIsStreaming(false);
        setMessages(msgs => [
          ...msgs,
          { id: Date.now().toString(), role: MessageRole.Error, content: message },
        ]);
      },
    });

    socketRef.current = socket;

    return () => {
      socket.close();
      socketRef.current = null;
    };
  }, [agentId, token, dispatch]);

  const sendMessage = useCallback((text: string) => {
    const socket = socketRef.current;
    if (!socket?.isOpen()) {
      toast.error('Not connected');
      return;
    }
    setMessages(prev => [
      ...prev,
      { id: Date.now().toString(), role: MessageRole.User, content: text },
    ]);
    setIsStreaming(true);
    setStreamingContent('');
    socket.send(text, conversationIdRef.current);
  }, []);

  const stopStreaming = useCallback(() => {
    socketRef.current?.stop();
  }, []);

  return {
    messages,
    streamingContent,
    isStreaming,
    conversationId,
    sendMessage,
    stopStreaming,
  };
};
