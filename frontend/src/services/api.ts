// Centralized API mock service
// All backend calls are mocked here for easy replacement with real API later

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

// Mock data
const mockUsers: User[] = [
  { id: '1', username: 'SnakeMaster', email: 'snake@test.com', highScore: 1250, gamesPlayed: 45, createdAt: new Date('2024-01-15') },
  { id: '2', username: 'PixelViper', email: 'pixel@test.com', highScore: 980, gamesPlayed: 32, createdAt: new Date('2024-02-20') },
  { id: '3', username: 'RetroGamer', email: 'retro@test.com', highScore: 875, gamesPlayed: 28, createdAt: new Date('2024-03-10') },
];

const mockLeaderboard: LeaderboardEntry[] = [
  { id: '1', username: 'SnakeMaster', score: 1250, mode: 'walls', date: new Date('2024-11-20') },
  { id: '2', username: 'PixelViper', score: 980, mode: 'pass-through', date: new Date('2024-11-19') },
  { id: '3', username: 'RetroGamer', score: 875, mode: 'walls', date: new Date('2024-11-18') },
  { id: '4', username: 'NeonNinja', score: 820, mode: 'pass-through', date: new Date('2024-11-17') },
  { id: '5', username: 'ArcadeKing', score: 750, mode: 'walls', date: new Date('2024-11-16') },
  { id: '6', username: 'GlitchRunner', score: 695, mode: 'pass-through', date: new Date('2024-11-15') },
  { id: '7', username: 'ByteHunter', score: 640, mode: 'walls', date: new Date('2024-11-14') },
  { id: '8', username: 'CodeSlayer', score: 590, mode: 'pass-through', date: new Date('2024-11-13') },
  { id: '9', username: 'DigitalDragon', score: 545, mode: 'walls', date: new Date('2024-11-12') },
  { id: '10', username: 'CyberSnake', score: 500, mode: 'pass-through', date: new Date('2024-11-11') },
];

const mockLivePlayers: LivePlayer[] = [
  {
    id: 'live1',
    username: 'NeonNinja',
    score: 340,
    mode: 'walls',
    snake: [{ x: 10, y: 10 }, { x: 9, y: 10 }, { x: 8, y: 10 }],
    food: { x: 15, y: 12 },
    direction: 'RIGHT',
    isAlive: true,
    watcherCount: 12,
  },
  {
    id: 'live2',
    username: 'GlitchRunner',
    score: 280,
    mode: 'pass-through',
    snake: [{ x: 5, y: 8 }, { x: 5, y: 7 }, { x: 5, y: 6 }],
    food: { x: 12, y: 5 },
    direction: 'DOWN',
    isAlive: true,
    watcherCount: 8,
  },
  {
    id: 'live3',
    username: 'ByteHunter',
    score: 195,
    mode: 'walls',
    snake: [{ x: 12, y: 15 }, { x: 11, y: 15 }, { x: 10, y: 15 }],
    food: { x: 3, y: 8 },
    direction: 'RIGHT',
    isAlive: true,
    watcherCount: 5,
  },
];

// Simulated network delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Auth API
export const authApi = {
  login: async (email: string, password: string): Promise<{ user: User; token: string }> => {
    await delay(500);
    const user = mockUsers.find(u => u.email === email);
    if (!user || password.length < 4) {
      throw new Error('Invalid credentials');
    }
    return { user, token: 'mock-jwt-token-' + user.id };
  },

  signup: async (username: string, email: string, password: string): Promise<{ user: User; token: string }> => {
    await delay(500);
    if (mockUsers.some(u => u.email === email)) {
      throw new Error('Email already exists');
    }
    if (mockUsers.some(u => u.username === username)) {
      throw new Error('Username already taken');
    }
    const newUser: User = {
      id: String(mockUsers.length + 1),
      username,
      email,
      highScore: 0,
      gamesPlayed: 0,
      createdAt: new Date(),
    };
    mockUsers.push(newUser);
    return { user: newUser, token: 'mock-jwt-token-' + newUser.id };
  },

  logout: async (): Promise<void> => {
    await delay(200);
  },

  getCurrentUser: async (token: string): Promise<User | null> => {
    await delay(300);
    const userId = token.replace('mock-jwt-token-', '');
    return mockUsers.find(u => u.id === userId) || null;
  },
};

// Leaderboard API
export const leaderboardApi = {
  getTopScores: async (limit: number = 10, mode?: 'walls' | 'pass-through'): Promise<LeaderboardEntry[]> => {
    await delay(300);
    let entries = [...mockLeaderboard];
    if (mode) {
      entries = entries.filter(e => e.mode === mode);
    }
    return entries.slice(0, limit);
  },

  submitScore: async (userId: string, score: GameScore): Promise<LeaderboardEntry> => {
    await delay(400);
    const user = mockUsers.find(u => u.id === userId);
    if (!user) throw new Error('User not found');
    
    const entry: LeaderboardEntry = {
      id: String(mockLeaderboard.length + 1),
      username: user.username,
      score: score.score,
      mode: score.mode,
      date: new Date(),
    };
    mockLeaderboard.push(entry);
    mockLeaderboard.sort((a, b) => b.score - a.score);
    
    if (score.score > user.highScore) {
      user.highScore = score.score;
    }
    user.gamesPlayed++;
    
    return entry;
  },

  getUserRank: async (userId: string): Promise<number> => {
    await delay(200);
    const user = mockUsers.find(u => u.id === userId);
    if (!user) return -1;
    const rank = mockLeaderboard.findIndex(e => e.username === user.username);
    return rank === -1 ? mockLeaderboard.length + 1 : rank + 1;
  },
};

// Live Players API
export const livePlayersApi = {
  getLivePlayers: async (): Promise<LivePlayer[]> => {
    await delay(300);
    return [...mockLivePlayers];
  },

  getPlayerStream: async (playerId: string): Promise<LivePlayer | null> => {
    await delay(200);
    return mockLivePlayers.find(p => p.id === playerId) || null;
  },

  joinAsWatcher: async (playerId: string): Promise<void> => {
    await delay(100);
    const player = mockLivePlayers.find(p => p.id === playerId);
    if (player) {
      player.watcherCount++;
    }
  },

  leaveAsWatcher: async (playerId: string): Promise<void> => {
    await delay(100);
    const player = mockLivePlayers.find(p => p.id === playerId);
    if (player && player.watcherCount > 0) {
      player.watcherCount--;
    }
  },

  // Simulate game state updates for watching
  subscribeToPlayer: (playerId: string, callback: (player: LivePlayer) => void): (() => void) => {
    const player = mockLivePlayers.find(p => p.id === playerId);
    if (!player) return () => {};

    const interval = setInterval(() => {
      if (!player.isAlive) {
        clearInterval(interval);
        return;
      }

      // Simulate snake movement
      const head = { ...player.snake[0] };
      switch (player.direction) {
        case 'UP': head.y--; break;
        case 'DOWN': head.y++; break;
        case 'LEFT': head.x--; break;
        case 'RIGHT': head.x++; break;
      }

      // Wrap around for simulation
      if (head.x < 0) head.x = 19;
      if (head.x >= 20) head.x = 0;
      if (head.y < 0) head.y = 19;
      if (head.y >= 20) head.y = 0;

      // Check food
      if (head.x === player.food.x && head.y === player.food.y) {
        player.score += 10;
        player.food = {
          x: Math.floor(Math.random() * 20),
          y: Math.floor(Math.random() * 20),
        };
        player.snake.unshift(head);
      } else {
        player.snake.unshift(head);
        player.snake.pop();
      }

      // Randomly change direction occasionally
      if (Math.random() < 0.1) {
        const directions: ('UP' | 'DOWN' | 'LEFT' | 'RIGHT')[] = ['UP', 'DOWN', 'LEFT', 'RIGHT'];
        const opposite = { UP: 'DOWN', DOWN: 'UP', LEFT: 'RIGHT', RIGHT: 'LEFT' };
        const validDirections = directions.filter(d => d !== opposite[player.direction]);
        player.direction = validDirections[Math.floor(Math.random() * validDirections.length)];
      }

      callback({ ...player, snake: [...player.snake] });
    }, 150);

    return () => clearInterval(interval);
  },
};

// User Profile API
export const userApi = {
  getProfile: async (userId: string): Promise<User | null> => {
    await delay(300);
    return mockUsers.find(u => u.id === userId) || null;
  },

  updateProfile: async (userId: string, updates: Partial<User>): Promise<User> => {
    await delay(400);
    const user = mockUsers.find(u => u.id === userId);
    if (!user) throw new Error('User not found');
    Object.assign(user, updates);
    return user;
  },

  getStats: async (userId: string): Promise<{ highScore: number; gamesPlayed: number; rank: number }> => {
    await delay(300);
    const user = mockUsers.find(u => u.id === userId);
    if (!user) throw new Error('User not found');
    const rank = await leaderboardApi.getUserRank(userId);
    return {
      highScore: user.highScore,
      gamesPlayed: user.gamesPlayed,
      rank,
    };
  },
};
