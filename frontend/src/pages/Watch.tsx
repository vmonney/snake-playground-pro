import { useEffect, useState, useCallback } from 'react';
import { Layout } from '@/components/Layout';
import { livePlayersApi, LivePlayer } from '@/services/api';
import { GameCanvas } from '@/components/GameCanvas';
import { Button } from '@/components/ui/button';
import { Eye, Users, ArrowLeft, Shield, Zap, Radio } from 'lucide-react';
import { GameState } from '@/game/snakeEngine';

const Watch = () => {
  const [livePlayers, setLivePlayers] = useState<LivePlayer[]>([]);
  const [selectedPlayer, setSelectedPlayer] = useState<LivePlayer | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [gameState, setGameState] = useState<GameState | null>(null);

  useEffect(() => {
    const fetchLivePlayers = async () => {
      setIsLoading(true);
      try {
        const players = await livePlayersApi.getLivePlayers();
        setLivePlayers(players);
      } catch (error) {
        console.error('Failed to fetch live players:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchLivePlayers();
    const interval = setInterval(fetchLivePlayers, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleSelectPlayer = useCallback(async (player: LivePlayer) => {
    setSelectedPlayer(player);
    await livePlayersApi.joinAsWatcher(player.id);

    // Convert live player to game state
    const initialGameState: GameState = {
      snake: player.snake,
      food: player.food,
      direction: player.direction,
      nextDirection: player.direction,
      score: player.score,
      status: 'playing',
      mode: player.mode,
      gridSize: 20,
      speed: 150,
    };
    setGameState(initialGameState);

    // Subscribe to player updates
    const unsubscribe = livePlayersApi.subscribeToPlayer(player.id, (updatedPlayer) => {
      setGameState((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          snake: updatedPlayer.snake,
          food: updatedPlayer.food,
          direction: updatedPlayer.direction,
          score: updatedPlayer.score,
          status: updatedPlayer.isAlive ? 'playing' : 'game-over',
        };
      });
      setSelectedPlayer(updatedPlayer);
    });

    return () => {
      unsubscribe();
      livePlayersApi.leaveAsWatcher(player.id);
    };
  }, []);

  const handleBackToList = async () => {
    if (selectedPlayer) {
      await livePlayersApi.leaveAsWatcher(selectedPlayer.id);
    }
    setSelectedPlayer(null);
    setGameState(null);
  };

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        {selectedPlayer && gameState ? (
          // Watching View
          <div className="max-w-2xl mx-auto">
            <Button
              variant="ghost"
              onClick={handleBackToList}
              className="mb-6 animate-fade-in"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to players
            </Button>

            <div className="text-center mb-6 animate-slide-up">
              <div className="flex items-center justify-center gap-2 mb-2">
                <Radio className="w-4 h-4 text-destructive animate-pulse" />
                <span className="text-destructive font-medium">LIVE</span>
              </div>
              <h2 className="font-pixel text-lg text-primary text-glow">
                {selectedPlayer.username}
              </h2>
              <div className="flex items-center justify-center gap-4 mt-2 text-muted-foreground">
                <span className="flex items-center gap-1">
                  {selectedPlayer.mode === 'walls' ? (
                    <Shield className="w-4 h-4" />
                  ) : (
                    <Zap className="w-4 h-4" />
                  )}
                  {selectedPlayer.mode}
                </span>
                <span className="flex items-center gap-1">
                  <Eye className="w-4 h-4" />
                  {selectedPlayer.watcherCount} watching
                </span>
              </div>
            </div>

            <div className="flex justify-center mb-6 animate-slide-up" style={{ animationDelay: '0.1s' }}>
              <div className="text-center">
                <p className="text-muted-foreground text-sm uppercase tracking-wider">Score</p>
                <p className="font-pixel text-3xl text-primary text-glow">{gameState.score}</p>
              </div>
            </div>

            <div className="flex justify-center animate-slide-up" style={{ animationDelay: '0.2s' }}>
              <GameCanvas gameState={gameState} cellSize={20} />
            </div>
          </div>
        ) : (
          // Players List View
          <div className="max-w-2xl mx-auto">
            <div className="text-center mb-8 animate-slide-up">
              <div className="w-20 h-20 mx-auto mb-4 rounded-2xl bg-accent/20 flex items-center justify-center glow-accent">
                <Eye className="w-10 h-10 text-accent" />
              </div>
              <h1 className="font-pixel text-xl sm:text-2xl text-primary text-glow mb-2">
                WATCH LIVE
              </h1>
              <p className="text-muted-foreground">Spectate other players in real-time</p>
            </div>

            <div className="space-y-4 animate-slide-up" style={{ animationDelay: '0.1s' }}>
              {isLoading ? (
                <div className="text-center py-12">
                  <div className="w-12 h-12 mx-auto border-4 border-primary border-t-transparent rounded-full animate-spin" />
                  <p className="mt-4 text-muted-foreground">Finding live games...</p>
                </div>
              ) : livePlayers.length === 0 ? (
                <div className="text-center py-12 arcade-border">
                  <Users className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">No live games right now</p>
                  <p className="text-sm text-muted-foreground mt-2">Check back later!</p>
                </div>
              ) : (
                livePlayers.map((player, index) => (
                  <button
                    key={player.id}
                    onClick={() => handleSelectPlayer(player)}
                    className="w-full arcade-border p-4 hover:bg-primary/5 transition-all duration-300 hover:scale-[1.02] text-left"
                    style={{ animationDelay: `${0.1 + index * 0.05}s` }}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-lg bg-primary/20 flex items-center justify-center">
                          <span className="text-2xl">🐍</span>
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <Radio className="w-3 h-3 text-destructive animate-pulse" />
                            <p className="font-medium text-foreground">{player.username}</p>
                          </div>
                          <div className="flex items-center gap-3 text-sm text-muted-foreground">
                            <span className="flex items-center gap-1">
                              {player.mode === 'walls' ? (
                                <Shield className="w-3 h-3" />
                              ) : (
                                <Zap className="w-3 h-3" />
                              )}
                              {player.mode}
                            </span>
                            <span className="flex items-center gap-1">
                              <Eye className="w-3 h-3" />
                              {player.watcherCount}
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-pixel text-lg text-primary text-glow">{player.score}</p>
                        <p className="text-xs text-muted-foreground uppercase">score</p>
                      </div>
                    </div>
                  </button>
                ))
              )}
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Watch;
