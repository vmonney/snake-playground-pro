import { useState, useEffect, useCallback, useRef } from 'react';
import {
  GameState,
  GameMode,
  createInitialState,
  moveSnake,
  changeDirection,
  startGame,
  pauseGame,
  resetGame,
  keyToDirection,
} from '@/game/snakeEngine';

export function useSnakeGame(initialMode: GameMode = 'walls') {
  const [gameState, setGameState] = useState<GameState>(() => createInitialState(initialMode));
  const gameLoopRef = useRef<number | null>(null);

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    const direction = keyToDirection(e.key);
    
    if (direction) {
      e.preventDefault();
      setGameState(prev => changeDirection(prev, direction));
    } else if (e.key === ' ' || e.key === 'Enter') {
      e.preventDefault();
      setGameState(prev => {
        if (prev.status === 'idle') {
          return startGame(prev);
        } else if (prev.status === 'playing' || prev.status === 'paused') {
          return pauseGame(prev);
        }
        return prev;
      });
    } else if (e.key === 'r' || e.key === 'R') {
      e.preventDefault();
      setGameState(prev => resetGame(prev.mode));
    }
  }, []);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  useEffect(() => {
    if (gameState.status === 'playing') {
      gameLoopRef.current = window.setInterval(() => {
        setGameState(prev => moveSnake(prev));
      }, gameState.speed);
    } else {
      if (gameLoopRef.current) {
        clearInterval(gameLoopRef.current);
        gameLoopRef.current = null;
      }
    }

    return () => {
      if (gameLoopRef.current) {
        clearInterval(gameLoopRef.current);
      }
    };
  }, [gameState.status, gameState.speed]);

  const start = useCallback(() => {
    setGameState(prev => startGame(prev));
  }, []);

  const pause = useCallback(() => {
    setGameState(prev => pauseGame(prev));
  }, []);

  const reset = useCallback((mode?: GameMode) => {
    setGameState(resetGame(mode || gameState.mode));
  }, [gameState.mode]);

  const setMode = useCallback((mode: GameMode) => {
    setGameState(resetGame(mode));
  }, []);

  return {
    gameState,
    start,
    pause,
    reset,
    setMode,
  };
}
