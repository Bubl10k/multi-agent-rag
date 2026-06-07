import { WsMessageType, type WsIncomingDone, type WsIncomingStop, type WsIncomingError } from '@/types/agentChat';

type AgentChatSocketCallbacks = {
  onToken: (token: string) => void;
  onDone: (payload: WsIncomingDone) => void;
  onStopped: (payload: WsIncomingStop) => void;
  onError: (message: string) => void;
};

const buildWsUrl = (agentId: string, token: string): string => {
  const apiBase = import.meta.env.VITE_API_BASE_URL;
  if (apiBase && apiBase.startsWith('http')) {
    const wsBase = apiBase.replace(/^http/, 'ws');
    return `${wsBase}/agents/${agentId}/chat?token=${token}`;
  }
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  return `${protocol}://${window.location.host}/api/agents/${agentId}/chat?token=${token}`;
};

type ParsedMessage =
  | { type: WsMessageType.Token; value: string }
  | { type: WsMessageType.Done; payload: WsIncomingDone }
  | { type: WsMessageType.Stopped; payload: WsIncomingStop }
  | { type: WsMessageType.Error; message: string };

const parseMessage = (raw: string): ParsedMessage => {
  try {
    const data = JSON.parse(raw) as WsIncomingDone | WsIncomingStop | WsIncomingError;
    if ('error' in data) return { type: WsMessageType.Error, message: data.error };
    if ('stopped' in data) return { type: WsMessageType.Stopped, payload: data };
    if ('done' in data) return { type: WsMessageType.Done, payload: data };
  } catch {
    // not JSON — plain text token
  }
  return { type: WsMessageType.Token, value: raw };
};

export class AgentChatSocket {
  private ws: WebSocket;

  constructor(
    agentId: string,
    token: string,
    callbacks: AgentChatSocketCallbacks,
    connectionErrorMessage = 'Connection error',
  ) {
    this.ws = new WebSocket(buildWsUrl(agentId, token));

    this.ws.onmessage = event => {
      const parsed = parseMessage(event.data as string);
      if (parsed.type === WsMessageType.Token) callbacks.onToken(parsed.value);
      else if (parsed.type === WsMessageType.Done) callbacks.onDone(parsed.payload);
      else if (parsed.type === WsMessageType.Stopped) callbacks.onStopped(parsed.payload);
      else callbacks.onError(parsed.message);
    };

    this.ws.onerror = () => callbacks.onError(connectionErrorMessage);
  }

  send(message: string, conversationId: string | null, language?: string): void {
    if (this.ws.readyState !== WebSocket.OPEN) {
      return;
    }
    this.ws.send(
      JSON.stringify({
        message,
        ...(conversationId ? { conversation_id: conversationId } : {}),
        ...(language ? { language } : {}),
      }),
    );
  }

  stop(): void {
    if (this.ws.readyState !== WebSocket.OPEN) return;
    this.ws.send(JSON.stringify({ type: WsMessageType.Stop }));
  }

  isOpen(): boolean {
    return this.ws.readyState === WebSocket.OPEN;
  }

  close(): void {
    this.ws.close();
  }
}
