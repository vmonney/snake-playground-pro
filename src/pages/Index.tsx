import { useState } from 'react';
import { Layout } from '@/components/Layout';
import { GameCanvas } from '@/components/GameCanvas';
import { useSnakeGame } from '@/hooks/useSnakeGame';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/contexts/AuthContext';
import { leaderboardApi } from '@/services/api';
import { toast } from 'sonner';
import { GameMode } from '@/game/snakeEngine';
import { Play, Pause, RotateCcw, Trophy, Zap, Shield } from 'lucide-react';

const Index = () => {
  const { gameState, start, pause, reset, setMode } = useSnakeGame('walls');
  const { user, isAuthenticated } = useAuth();
  const [submittingScore, setSubmittingScore] = useState(false);

  const handleModeChange = (mode: GameMode) => {
    setMode(mode);
  };

  const handleSubmitScore = async () => {
    if (!isAuthenticated || !user) {
      toast.error('Please login to submit your score');
      return;
    }

    setSubmittingScore(true);
    try {
      await leaderboardApi.submitScore(user.id, {
        score: gameState.score,
        mode: gameState.mode,
      });
      toast.success('Score submitted to leaderboard!');
    } catch (error) {
      toast.error('Failed to submit score');
    } finally {
      setSubmittingScore(false);
    }
  };

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col items-center gap-8">
          {/* Title */}
          <div className="text-center animate-slide-up">
            <h1 className="font-pixel text-2xl sm:text-3xl text-primary text-glow mb-2">
              SNAKE GAME
            </h1>
            <p className="text-muted-foreground">
              Use arrow keys or WASD to move • Space to pause
            </p>
          </div>

          {/* Mode Selection */}
          <div className="flex gap-4 animate-slide-up" style={{ animationDelay: '0.1s' }}>
            <Button
              variant={gameState.mode === 'walls' ? 'default' : 'outline'}
              onClick={() => handleModeChange('walls')}
              className="flex items-center gap-2"
              disabled={gameState.status === 'playing'}
            >
              <Shield className="w-4 h-4" />
              Walls Mode
            </Button>
            <Button
              variant={gameState.mode === 'pass-through' ? 'default' : 'outline'}
              onClick={() => handleModeChange('pass-through')}
              className="flex items-center gap-2"
              disabled={gameState.status === 'playing'}
            >
              <Zap className="w-4 h-4" />
              Pass-Through
            </Button>
          </div>

          {/* Score Display */}
          <div className="flex items-center gap-8 animate-slide-up" style={{ animationDelay: '0.2s' }}>
            <div className="text-center">
              <p className="text-muted-foreground text-sm uppercase tracking-wider">Score</p>
              <p className="font-pixel text-2xl text-primary text-glow">{gameState.score}</p>
            </div>
            <div className="text-center">
              <p className="text-muted-foreground text-sm uppercase tracking-wider">Length</p>
              <p className="font-pixel text-2xl text-accent text-glow-accent">{gameState.snake.length}</p>
            </div>
          </div>

          {/* Game Canvas */}
          <div className="animate-slide-up" style={{ animationDelay: '0.3s' }}>
            <GameCanvas gameState={gameState} cellSize={20} />
          </div>

          {/* Controls */}
          <div className="flex gap-4 animate-slide-up" style={{ animationDelay: '0.4s' }}>
            {gameState.status === 'idle' && (
              <Button variant="arcade" size="lg" onClick={start}>
                <Play className="w-5 h-5" />
                Start
              </Button>
            )}
            
            {gameState.status === 'playing' && (
              <Button variant="arcade" size="lg" onClick={pause}>
                <Pause className="w-5 h-5" />
                Pause
              </Button>
            )}
            
            {gameState.status === 'paused' && (
              <Button variant="arcade" size="lg" onClick={start}>
                <Play className="w-5 h-5" />
                Resume
              </Button>
            )}

            {gameState.status === 'game-over' && (
              <>
                <Button variant="arcade" size="lg" onClick={() => reset()}>
                  <RotateCcw className="w-5 h-5" />
                  Play Again
                </Button>
                {gameState.score > 0 && (
                  <Button
                    variant="accent"
                    size="lg"
                    onClick={handleSubmitScore}
                    disabled={submittingScore || !isAuthenticated}
                  >
                    <Trophy className="w-5 h-5" />
                    {submittingScore ? 'Submitting...' : 'Submit Score'}
                  </Button>
                )}
              </>
            )}

            {(gameState.status === 'playing' || gameState.status === 'paused') && (
              <Button variant="outline" size="lg" onClick={() => reset()}>
                <RotateCcw className="w-5 h-5" />
                Reset
              </Button>
            )}
          </div>

          {/* Instructions */}
          <div className="arcade-border p-6 max-w-md text-center animate-slide-up" style={{ animationDelay: '0.5s' }}>
            <h3 className="font-pixel text-xs text-primary mb-4">HOW TO PLAY</h3>
            <div className="grid grid-cols-2 gap-4 text-sm text-muted-foreground">
              <div>
                <p className="text-foreground">Movement</p>
                <p>Arrow Keys / WASD</p>
              </div>
              <div>
                <p className="text-foreground">Pause</p>
                <p>Spacebar</p>
              </div>
              <div>
                <p className="text-foreground">Restart</p>
                <p>R Key</p>
              </div>
              <div>
                <p className="text-foreground">Mode</p>
                <p>{gameState.mode === 'walls' ? 'Walls kill' : 'Wrap around'}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Index;
