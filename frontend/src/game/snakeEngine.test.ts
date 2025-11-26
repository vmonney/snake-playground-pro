import { describe, it, expect } from 'vitest';
import {
  createInitialState,
  moveSnake,
  changeDirection,
  startGame,
  pauseGame,
  resetGame,
  isValidDirectionChange,
  getOppositeDirection,
  keyToDirection,
  generateFood,
  GRID_SIZE,
  POINTS_PER_FOOD,
} from './snakeEngine';

describe('Snake Engine', () => {
  describe('createInitialState', () => {
    it('should create initial state with correct defaults', () => {
      const state = createInitialState('walls');
      
      expect(state.status).toBe('idle');
      expect(state.score).toBe(0);
      expect(state.direction).toBe('RIGHT');
      expect(state.snake.length).toBe(3);
      expect(state.mode).toBe('walls');
      expect(state.gridSize).toBe(GRID_SIZE);
    });

    it('should create state with pass-through mode', () => {
      const state = createInitialState('pass-through');
      expect(state.mode).toBe('pass-through');
    });

    it('should place snake in the center', () => {
      const state = createInitialState('walls');
      const centerY = Math.floor(GRID_SIZE / 2);
      
      state.snake.forEach(segment => {
        expect(segment.y).toBe(centerY);
      });
    });
  });

  describe('generateFood', () => {
    it('should generate food not on snake', () => {
      const snake = [{ x: 5, y: 5 }, { x: 4, y: 5 }];
      const food = generateFood(snake);
      
      const isOnSnake = snake.some(s => s.x === food.x && s.y === food.y);
      expect(isOnSnake).toBe(false);
    });

    it('should generate food within grid bounds', () => {
      const snake = [{ x: 5, y: 5 }];
      for (let i = 0; i < 100; i++) {
        const food = generateFood(snake);
        expect(food.x).toBeGreaterThanOrEqual(0);
        expect(food.x).toBeLessThan(GRID_SIZE);
        expect(food.y).toBeGreaterThanOrEqual(0);
        expect(food.y).toBeLessThan(GRID_SIZE);
      }
    });
  });

  describe('getOppositeDirection', () => {
    it('should return correct opposite directions', () => {
      expect(getOppositeDirection('UP')).toBe('DOWN');
      expect(getOppositeDirection('DOWN')).toBe('UP');
      expect(getOppositeDirection('LEFT')).toBe('RIGHT');
      expect(getOppositeDirection('RIGHT')).toBe('LEFT');
    });
  });

  describe('isValidDirectionChange', () => {
    it('should allow perpendicular direction changes', () => {
      expect(isValidDirectionChange('RIGHT', 'UP')).toBe(true);
      expect(isValidDirectionChange('RIGHT', 'DOWN')).toBe(true);
      expect(isValidDirectionChange('UP', 'LEFT')).toBe(true);
      expect(isValidDirectionChange('UP', 'RIGHT')).toBe(true);
    });

    it('should not allow opposite direction changes', () => {
      expect(isValidDirectionChange('RIGHT', 'LEFT')).toBe(false);
      expect(isValidDirectionChange('UP', 'DOWN')).toBe(false);
      expect(isValidDirectionChange('LEFT', 'RIGHT')).toBe(false);
      expect(isValidDirectionChange('DOWN', 'UP')).toBe(false);
    });

    it('should allow same direction', () => {
      expect(isValidDirectionChange('RIGHT', 'RIGHT')).toBe(true);
      expect(isValidDirectionChange('UP', 'UP')).toBe(true);
    });
  });

  describe('moveSnake', () => {
    it('should not move when status is not playing', () => {
      const state = createInitialState('walls');
      const newState = moveSnake(state);
      
      expect(newState.snake).toEqual(state.snake);
    });

    it('should move snake in current direction', () => {
      let state = createInitialState('walls');
      state = startGame(state);
      const initialHead = { ...state.snake[0] };
      
      const newState = moveSnake(state);
      
      expect(newState.snake[0].x).toBe(initialHead.x + 1);
      expect(newState.snake[0].y).toBe(initialHead.y);
    });

    it('should handle wall collision in walls mode', () => {
      let state = createInitialState('walls');
      state = {
        ...state,
        snake: [{ x: GRID_SIZE - 1, y: 5 }, { x: GRID_SIZE - 2, y: 5 }],
        direction: 'RIGHT',
        nextDirection: 'RIGHT',
        status: 'playing',
      };
      
      const newState = moveSnake(state);
      
      expect(newState.status).toBe('game-over');
    });

    it('should wrap around in pass-through mode', () => {
      let state = createInitialState('pass-through');
      state = {
        ...state,
        snake: [{ x: GRID_SIZE - 1, y: 5 }, { x: GRID_SIZE - 2, y: 5 }],
        direction: 'RIGHT',
        nextDirection: 'RIGHT',
        status: 'playing',
      };
      
      const newState = moveSnake(state);
      
      expect(newState.status).toBe('playing');
      expect(newState.snake[0].x).toBe(0);
    });

    it('should increase score when eating food', () => {
      let state = createInitialState('walls');
      state = {
        ...state,
        snake: [{ x: 5, y: 5 }, { x: 4, y: 5 }],
        food: { x: 6, y: 5 },
        direction: 'RIGHT',
        nextDirection: 'RIGHT',
        status: 'playing',
      };
      
      const newState = moveSnake(state);
      
      expect(newState.score).toBe(POINTS_PER_FOOD);
      expect(newState.snake.length).toBe(3);
    });

    it('should detect self-collision', () => {
      let state = createInitialState('walls');
      state = {
        ...state,
        snake: [
          { x: 5, y: 5 },
          { x: 6, y: 5 },
          { x: 6, y: 6 },
          { x: 5, y: 6 },
          { x: 4, y: 6 },
        ],
        direction: 'DOWN',
        nextDirection: 'DOWN',
        status: 'playing',
      };
      
      const newState = moveSnake(state);
      
      expect(newState.status).toBe('game-over');
    });
  });

  describe('changeDirection', () => {
    it('should change direction when valid', () => {
      let state = createInitialState('walls');
      state = startGame(state);
      
      const newState = changeDirection(state, 'UP');
      
      expect(newState.nextDirection).toBe('UP');
    });

    it('should not change to opposite direction', () => {
      let state = createInitialState('walls');
      state = startGame(state);
      
      const newState = changeDirection(state, 'LEFT');
      
      expect(newState.nextDirection).toBe('RIGHT');
    });

    it('should not change direction when not playing', () => {
      const state = createInitialState('walls');
      
      const newState = changeDirection(state, 'UP');
      
      expect(newState.nextDirection).toBe('RIGHT');
    });
  });

  describe('startGame', () => {
    it('should set status to playing', () => {
      const state = createInitialState('walls');
      const newState = startGame(state);
      
      expect(newState.status).toBe('playing');
    });
  });

  describe('pauseGame', () => {
    it('should toggle between playing and paused', () => {
      let state = createInitialState('walls');
      state = startGame(state);
      
      let pausedState = pauseGame(state);
      expect(pausedState.status).toBe('paused');
      
      let resumedState = pauseGame(pausedState);
      expect(resumedState.status).toBe('playing');
    });

    it('should not affect idle or game-over states', () => {
      const idleState = createInitialState('walls');
      expect(pauseGame(idleState).status).toBe('idle');
      
      const gameOverState = { ...idleState, status: 'game-over' as const };
      expect(pauseGame(gameOverState).status).toBe('game-over');
    });
  });

  describe('resetGame', () => {
    it('should reset to initial state with specified mode', () => {
      const state = resetGame('pass-through');
      
      expect(state.status).toBe('idle');
      expect(state.score).toBe(0);
      expect(state.mode).toBe('pass-through');
    });
  });

  describe('keyToDirection', () => {
    it('should map arrow keys correctly', () => {
      expect(keyToDirection('ArrowUp')).toBe('UP');
      expect(keyToDirection('ArrowDown')).toBe('DOWN');
      expect(keyToDirection('ArrowLeft')).toBe('LEFT');
      expect(keyToDirection('ArrowRight')).toBe('RIGHT');
    });

    it('should map WASD keys correctly', () => {
      expect(keyToDirection('w')).toBe('UP');
      expect(keyToDirection('W')).toBe('UP');
      expect(keyToDirection('s')).toBe('DOWN');
      expect(keyToDirection('a')).toBe('LEFT');
      expect(keyToDirection('d')).toBe('RIGHT');
    });

    it('should return null for unknown keys', () => {
      expect(keyToDirection('x')).toBe(null);
      expect(keyToDirection('Enter')).toBe(null);
    });
  });
});
