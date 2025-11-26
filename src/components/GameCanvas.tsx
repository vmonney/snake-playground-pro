import { useEffect, useRef, useCallback } from 'react';
import { GameState, Position } from '@/game/snakeEngine';

interface GameCanvasProps {
  gameState: GameState;
  cellSize?: number;
  className?: string;
}

export function GameCanvas({ gameState, cellSize = 20, className = '' }: GameCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const { snake, food, gridSize, status } = gameState;
    const width = gridSize * cellSize;
    const height = gridSize * cellSize;

    // Clear canvas
    ctx.fillStyle = 'hsl(220, 20%, 8%)';
    ctx.fillRect(0, 0, width, height);

    // Draw grid lines (subtle)
    ctx.strokeStyle = 'hsl(220, 20%, 12%)';
    ctx.lineWidth = 1;
    for (let i = 0; i <= gridSize; i++) {
      ctx.beginPath();
      ctx.moveTo(i * cellSize, 0);
      ctx.lineTo(i * cellSize, height);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(0, i * cellSize);
      ctx.lineTo(width, i * cellSize);
      ctx.stroke();
    }

    // Draw food with glow effect
    const foodX = food.x * cellSize + cellSize / 2;
    const foodY = food.y * cellSize + cellSize / 2;
    const foodRadius = cellSize / 2 - 2;

    // Food glow
    const gradient = ctx.createRadialGradient(foodX, foodY, 0, foodX, foodY, foodRadius * 2);
    gradient.addColorStop(0, 'hsla(0, 100%, 60%, 0.6)');
    gradient.addColorStop(1, 'hsla(0, 100%, 60%, 0)');
    ctx.fillStyle = gradient;
    ctx.fillRect(food.x * cellSize - cellSize / 2, food.y * cellSize - cellSize / 2, cellSize * 2, cellSize * 2);

    // Food body
    ctx.fillStyle = 'hsl(0, 100%, 50%)';
    ctx.shadowColor = 'hsl(0, 100%, 50%)';
    ctx.shadowBlur = 10;
    ctx.beginPath();
    ctx.arc(foodX, foodY, foodRadius, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0;

    // Draw snake
    snake.forEach((segment: Position, index: number) => {
      const x = segment.x * cellSize;
      const y = segment.y * cellSize;
      const isHead = index === 0;

      // Snake glow (head glows more)
      ctx.shadowColor = 'hsl(150, 100%, 50%)';
      ctx.shadowBlur = isHead ? 15 : 8;

      // Snake body color gradient from head to tail
      const brightness = 50 - (index / snake.length) * 20;
      ctx.fillStyle = `hsl(150, 100%, ${brightness}%)`;

      // Rounded rectangle for snake segments
      const radius = 4;
      const padding = 1;
      ctx.beginPath();
      ctx.roundRect(x + padding, y + padding, cellSize - padding * 2, cellSize - padding * 2, radius);
      ctx.fill();

      // Draw eyes on head
      if (isHead) {
        ctx.shadowBlur = 0;
        ctx.fillStyle = 'hsl(220, 20%, 6%)';
        const eyeSize = 3;
        const eyeOffset = 5;

        let eye1X = x + cellSize / 2 - eyeOffset;
        let eye1Y = y + cellSize / 2 - eyeOffset;
        let eye2X = x + cellSize / 2 + eyeOffset;
        let eye2Y = y + cellSize / 2 - eyeOffset;

        // Adjust eye position based on direction
        switch (gameState.direction) {
          case 'UP':
            eye1Y = y + eyeOffset;
            eye2Y = y + eyeOffset;
            break;
          case 'DOWN':
            eye1Y = y + cellSize - eyeOffset;
            eye2Y = y + cellSize - eyeOffset;
            break;
          case 'LEFT':
            eye1X = x + eyeOffset;
            eye2X = x + eyeOffset;
            eye1Y = y + cellSize / 2 - 3;
            eye2Y = y + cellSize / 2 + 3;
            break;
          case 'RIGHT':
            eye1X = x + cellSize - eyeOffset;
            eye2X = x + cellSize - eyeOffset;
            eye1Y = y + cellSize / 2 - 3;
            eye2Y = y + cellSize / 2 + 3;
            break;
        }

        ctx.beginPath();
        ctx.arc(eye1X, eye1Y, eyeSize, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.arc(eye2X, eye2Y, eyeSize, 0, Math.PI * 2);
        ctx.fill();
      }
    });

    ctx.shadowBlur = 0;

    // Draw game over overlay
    if (status === 'game-over') {
      ctx.fillStyle = 'hsla(220, 20%, 6%, 0.8)';
      ctx.fillRect(0, 0, width, height);

      ctx.fillStyle = 'hsl(0, 100%, 50%)';
      ctx.shadowColor = 'hsl(0, 100%, 50%)';
      ctx.shadowBlur = 20;
      ctx.font = 'bold 24px "Press Start 2P", monospace';
      ctx.textAlign = 'center';
      ctx.fillText('GAME OVER', width / 2, height / 2);
      ctx.shadowBlur = 0;
    }

    // Draw paused overlay
    if (status === 'paused') {
      ctx.fillStyle = 'hsla(220, 20%, 6%, 0.7)';
      ctx.fillRect(0, 0, width, height);

      ctx.fillStyle = 'hsl(150, 100%, 50%)';
      ctx.shadowColor = 'hsl(150, 100%, 50%)';
      ctx.shadowBlur = 15;
      ctx.font = 'bold 20px "Press Start 2P", monospace';
      ctx.textAlign = 'center';
      ctx.fillText('PAUSED', width / 2, height / 2);
      ctx.shadowBlur = 0;
    }

    // Draw idle state
    if (status === 'idle') {
      ctx.fillStyle = 'hsla(220, 20%, 6%, 0.5)';
      ctx.fillRect(0, 0, width, height);

      ctx.fillStyle = 'hsl(150, 100%, 50%)';
      ctx.shadowColor = 'hsl(150, 100%, 50%)';
      ctx.shadowBlur = 15;
      ctx.font = '14px "Press Start 2P", monospace';
      ctx.textAlign = 'center';
      ctx.fillText('PRESS SPACE', width / 2, height / 2 - 10);
      ctx.fillText('TO START', width / 2, height / 2 + 15);
      ctx.shadowBlur = 0;
    }
  }, [gameState, cellSize]);

  useEffect(() => {
    draw();
  }, [draw]);

  return (
    <canvas
      ref={canvasRef}
      width={gameState.gridSize * cellSize}
      height={gameState.gridSize * cellSize}
      className={`game-canvas ${className}`}
    />
  );
}
