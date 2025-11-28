import { getWebSocketUrl } from './utils';

export interface WebSocketMessage {
  type: 'gameState' | 'gameOver';
  data: {
    snake: { x: number; y: number }[];
    food: { x: number; y: number };
    direction: 'UP' | 'DOWN' | 'LEFT' | 'RIGHT';
    score: number;
    isAlive: boolean;
  };
}

type MessageCallback = (message: WebSocketMessage) => void;
type ErrorCallback = (error: Event) => void;
type CloseCallback = (event: CloseEvent) => void;

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private playerId: string;
  private baseUrl: string;
  private messageCallbacks: MessageCallback[] = [];
  private errorCallbacks: ErrorCallback[] = [];
  private closeCallbacks: CloseCallback[] = [];
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second
  private reconnectTimer: NodeJS.Timeout | null = null;
  private isIntentionallyClosed = false;

  constructor(playerId: string, baseUrl?: string) {
    this.playerId = playerId;
    // Use provided base URL or get from environment
    const httpUrl = baseUrl || import.meta.env.VITE_API_BASE_URL.replace('/api/v1', '');
    this.baseUrl = getWebSocketUrl(httpUrl);
  }

  connect(): void {
    this.isIntentionallyClosed = false;
    const wsUrl = `${this.baseUrl}/api/v1/live/players/${this.playerId}/stream`;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log(`WebSocket connected to player ${this.playerId}`);
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          this.messageCallbacks.forEach((callback) => callback(message));
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.errorCallbacks.forEach((callback) => callback(error));
      };

      this.ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason);
        this.closeCallbacks.forEach((callback) => callback(event));

        // Attempt reconnection if not intentionally closed
        if (!this.isIntentionallyClosed && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

          console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

          this.reconnectTimer = setTimeout(() => {
            this.connect();
          }, delay);
        }
      };
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
    }
  }

  disconnect(): void {
    this.isIntentionallyClosed = true;

    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  onMessage(callback: MessageCallback): void {
    this.messageCallbacks.push(callback);
  }

  onError(callback: ErrorCallback): void {
    this.errorCallbacks.push(callback);
  }

  onClose(callback: CloseCallback): void {
    this.closeCallbacks.push(callback);
  }

  removeMessageCallback(callback: MessageCallback): void {
    this.messageCallbacks = this.messageCallbacks.filter((cb) => cb !== callback);
  }

  removeErrorCallback(callback: ErrorCallback): void {
    this.errorCallbacks = this.errorCallbacks.filter((cb) => cb !== callback);
  }

  removeCloseCallback(callback: CloseCallback): void {
    this.closeCallbacks = this.closeCallbacks.filter((cb) => cb !== callback);
  }

  getReadyState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED;
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}
