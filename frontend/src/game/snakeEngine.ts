// Snake Game Engine - Core game logic

export type Direction = 'UP' | 'DOWN' | 'LEFT' | 'RIGHT';
export type GameMode = 'walls' | 'pass-through';
export type GameStatus = 'idle' | 'playing' | 'paused' | 'game-over';

export interface Position {
  x: number;
  y: number;
}

export interface GameState {
  snake: Position[];
  food: Position;
  direction: Direction;
  nextDirection: Direction;
  score: number;
  status: GameStatus;
  mode: GameMode;
  gridSize: number;
  speed: number;
}

export const INITIAL_SPEED = 150;
export const SPEED_INCREMENT = 5;
export const MIN_SPEED = 50;
export const GRID_SIZE = 20;
export const POINTS_PER_FOOD = 10;

export function createInitialState(mode: GameMode = 'walls'): GameState {
  const centerX = Math.floor(GRID_SIZE / 2);
  const centerY = Math.floor(GRID_SIZE / 2);

  return {
    snake: [
      { x: centerX, y: centerY },
      { x: centerX - 1, y: centerY },
      { x: centerX - 2, y: centerY },
    ],
    food: generateFood([
      { x: centerX, y: centerY },
      { x: centerX - 1, y: centerY },
      { x: centerX - 2, y: centerY },
    ]),
    direction: 'RIGHT',
    nextDirection: 'RIGHT',
    score: 0,
    status: 'idle',
    mode,
    gridSize: GRID_SIZE,
    speed: INITIAL_SPEED,
  };
}

export function generateFood(snake: Position[]): Position {
  let food: Position;
  do {
    food = {
      x: Math.floor(Math.random() * GRID_SIZE),
      y: Math.floor(Math.random() * GRID_SIZE),
    };
  } while (snake.some(segment => segment.x === food.x && segment.y === food.y));
  return food;
}

export function getOppositeDirection(direction: Direction): Direction {
  const opposites: Record<Direction, Direction> = {
    UP: 'DOWN',
    DOWN: 'UP',
    LEFT: 'RIGHT',
    RIGHT: 'LEFT',
  };
  return opposites[direction];
}

export function isValidDirectionChange(current: Direction, next: Direction): boolean {
  return next !== getOppositeDirection(current);
}

export function moveSnake(state: GameState): GameState {
  if (state.status !== 'playing') return state;

  const { snake, food, nextDirection, mode, gridSize } = state;
  const head = snake[0];

  // Calculate new head position
  let newHead: Position;
  switch (nextDirection) {
    case 'UP':
      newHead = { x: head.x, y: head.y - 1 };
      break;
    case 'DOWN':
      newHead = { x: head.x, y: head.y + 1 };
      break;
    case 'LEFT':
      newHead = { x: head.x - 1, y: head.y };
      break;
    case 'RIGHT':
      newHead = { x: head.x + 1, y: head.y };
      break;
  }

  // Handle wall collision based on mode
  if (mode === 'walls') {
    if (newHead.x < 0 || newHead.x >= gridSize || newHead.y < 0 || newHead.y >= gridSize) {
      return { ...state, status: 'game-over' };
    }
  } else {
    // Pass-through mode: wrap around
    if (newHead.x < 0) newHead.x = gridSize - 1;
    if (newHead.x >= gridSize) newHead.x = 0;
    if (newHead.y < 0) newHead.y = gridSize - 1;
    if (newHead.y >= gridSize) newHead.y = 0;
  }

  // Check self-collision (exclude tail if not eating)
  const willEat = newHead.x === food.x && newHead.y === food.y;
  const checkSegments = willEat ? snake : snake.slice(0, -1);
  if (checkSegments.some(segment => segment.x === newHead.x && segment.y === newHead.y)) {
    return { ...state, status: 'game-over' };
  }

  // Build new snake
  const newSnake = [newHead, ...snake];
  let newFood = food;
  let newScore = state.score;
  let newSpeed = state.speed;

  if (willEat) {
    newScore += POINTS_PER_FOOD;
    newFood = generateFood(newSnake);
    newSpeed = Math.max(MIN_SPEED, state.speed - SPEED_INCREMENT);
  } else {
    newSnake.pop();
  }

  return {
    ...state,
    snake: newSnake,
    food: newFood,
    direction: nextDirection,
    score: newScore,
    speed: newSpeed,
  };
}

export function changeDirection(state: GameState, newDirection: Direction): GameState {
  if (state.status !== 'playing') return state;
  
  if (isValidDirectionChange(state.direction, newDirection)) {
    return { ...state, nextDirection: newDirection };
  }
  return state;
}

export function startGame(state: GameState): GameState {
  return { ...state, status: 'playing' };
}

export function pauseGame(state: GameState): GameState {
  if (state.status === 'playing') {
    return { ...state, status: 'paused' };
  }
  if (state.status === 'paused') {
    return { ...state, status: 'playing' };
  }
  return state;
}

export function resetGame(mode: GameMode): GameState {
  return createInitialState(mode);
}

// Key mapping
export function keyToDirection(key: string): Direction | null {
  const keyMap: Record<string, Direction> = {
    ArrowUp: 'UP',
    ArrowDown: 'DOWN',
    ArrowLeft: 'LEFT',
    ArrowRight: 'RIGHT',
    w: 'UP',
    W: 'UP',
    s: 'DOWN',
    S: 'DOWN',
    a: 'LEFT',
    A: 'LEFT',
    d: 'RIGHT',
    D: 'RIGHT',
  };
  return keyMap[key] || null;
}
