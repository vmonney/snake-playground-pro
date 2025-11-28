// Centralized API service
// All backend calls use real HTTP client
import apiClient from './apiClient';
import { parseDate } from './utils';
import { WebSocketClient } from './websocketClient';

export interface User {
  id: string;
  username: string;
  email: string;
  highScore: number;
  gamesPlayed: number;
  createdAt: Date;
}

export interface LeaderboardEntry {
  id: string;
  username: string;
  score: number;
  mode: 'walls' | 'pass-through';
  date: Date;
}

export interface LivePlayer {
  id: string;
  username: string;
  score: number;
  mode: 'walls' | 'pass-through';
  snake: { x: number; y: number }[];
  food: { x: number; y: number };
  direction: 'UP' | 'DOWN' | 'LEFT' | 'RIGHT';
  isAlive: boolean;
  watcherCount: number;
}

export interface GameScore {
  score: number;
  mode: 'walls' | 'pass-through';
}

// Auth API
export const authApi = {
  login: async (email: string, password: string): Promise<{ user: User; token: string }> => {
    const response = await apiClient.post('/auth/login', { email, password });
    const data = response.data;
    return {
      user: {
        ...data.user,
        createdAt: parseDate(data.user.createdAt),
      },
      token: data.token,
    };
  },

  signup: async (username: string, email: string, password: string): Promise<{ user: User; token: string }> => {
    const response = await apiClient.post('/auth/signup', { username, email, password });
    const data = response.data;
    return {
      user: {
        ...data.user,
        createdAt: parseDate(data.user.createdAt),
      },
      token: data.token,
    };
  },

  logout: async (): Promise<void> => {
    await apiClient.post('/auth/logout');
  },

  getCurrentUser: async (token: string): Promise<User | null> => {
    try {
      const response = await apiClient.get('/auth/me');
      const data = response.data;
      return {
        ...data,
        createdAt: parseDate(data.createdAt),
      };
    } catch (error) {
      return null;
    }
  },
};

// Leaderboard API
export const leaderboardApi = {
  getTopScores: async (limit: number = 10, mode?: 'walls' | 'pass-through'): Promise<LeaderboardEntry[]> => {
    const params: any = { limit };
    if (mode) {
      params.mode = mode;
    }
    const response = await apiClient.get('/leaderboard', { params });
    return response.data.map((entry: any) => ({
      ...entry,
      date: parseDate(entry.date),
    }));
  },

  submitScore: async (userId: string, score: GameScore): Promise<LeaderboardEntry> => {
    const response = await apiClient.post('/leaderboard/scores', score);
    const data = response.data;
    return {
      ...data,
      date: parseDate(data.date),
    };
  },

  getUserRank: async (userId: string): Promise<number> => {
    const response = await apiClient.get(`/leaderboard/rank/${userId}`);
    return response.data.rank;
  },
};

// Live Players API
export const livePlayersApi = {
  getLivePlayers: async (): Promise<LivePlayer[]> => {
    const response = await apiClient.get('/live/players');
    return response.data;
  },

  getPlayerStream: async (playerId: string): Promise<LivePlayer | null> => {
    try {
      const response = await apiClient.get(`/live/players/${playerId}`);
      return response.data;
    } catch (error) {
      return null;
    }
  },

  joinAsWatcher: async (playerId: string): Promise<void> => {
    await apiClient.post(`/live/players/${playerId}/watch`);
  },

  leaveAsWatcher: async (playerId: string): Promise<void> => {
    await apiClient.delete(`/live/players/${playerId}/watch`);
  },

  // WebSocket subscription for real-time game updates
  subscribeToPlayer: (playerId: string, callback: (player: LivePlayer) => void): (() => void) => {
    const wsClient = new WebSocketClient(playerId);

    wsClient.onMessage((message) => {
      // Convert WebSocket message to LivePlayer update
      const updatedPlayer: Partial<LivePlayer> = {
        snake: message.data.snake,
        food: message.data.food,
        direction: message.data.direction,
        score: message.data.score,
        isAlive: message.data.isAlive,
      };

      // Fetch the full player data to get additional fields
      livePlayersApi.getPlayerStream(playerId).then((player) => {
        if (player) {
          callback({
            ...player,
            ...updatedPlayer,
          });
        }
      });
    });

    wsClient.onError((error) => {
      console.error('WebSocket error for player', playerId, error);
    });

    wsClient.connect();

    // Return cleanup function
    return () => {
      wsClient.disconnect();
    };
  },
};

// User Profile API
export const userApi = {
  getProfile: async (userId: string): Promise<User | null> => {
    try {
      const response = await apiClient.get(`/users/${userId}`);
      const data = response.data;
      return {
        ...data,
        createdAt: parseDate(data.createdAt),
      };
    } catch (error) {
      return null;
    }
  },

  updateProfile: async (userId: string, updates: Partial<User>): Promise<User> => {
    const response = await apiClient.patch(`/users/${userId}`, {
      username: updates.username,
    });
    const data = response.data;
    return {
      ...data,
      createdAt: parseDate(data.createdAt),
    };
  },

  getStats: async (userId: string): Promise<{ highScore: number; gamesPlayed: number; rank: number }> => {
    const response = await apiClient.get(`/users/${userId}/stats`);
    return response.data;
  },
};
