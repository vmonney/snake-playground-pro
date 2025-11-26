import { useEffect, useState } from 'react';
import { Layout } from '@/components/Layout';
import { leaderboardApi, LeaderboardEntry } from '@/services/api';
import { Button } from '@/components/ui/button';
import { Trophy, Medal, Award, Calendar, Zap, Shield } from 'lucide-react';
import { GameMode } from '@/game/snakeEngine';

const Leaderboard = () => {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filterMode, setFilterMode] = useState<GameMode | 'all'>('all');

  useEffect(() => {
    const fetchLeaderboard = async () => {
      setIsLoading(true);
      try {
        const mode = filterMode === 'all' ? undefined : filterMode;
        const data = await leaderboardApi.getTopScores(10, mode);
        setEntries(data);
      } catch (error) {
        console.error('Failed to fetch leaderboard:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchLeaderboard();
  }, [filterMode]);

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return <Trophy className="w-6 h-6 text-yellow-500" />;
      case 2:
        return <Medal className="w-6 h-6 text-gray-400" />;
      case 3:
        return <Award className="w-6 h-6 text-amber-600" />;
      default:
        return <span className="w-6 h-6 flex items-center justify-center text-muted-foreground font-bold">{rank}</span>;
    }
  };

  const getRankStyle = (rank: number) => {
    switch (rank) {
      case 1:
        return 'bg-yellow-500/10 border-yellow-500/30';
      case 2:
        return 'bg-gray-400/10 border-gray-400/30';
      case 3:
        return 'bg-amber-600/10 border-amber-600/30';
      default:
        return 'bg-secondary/50 border-border';
    }
  };

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8 animate-slide-up">
            <div className="w-20 h-20 mx-auto mb-4 rounded-2xl bg-primary/20 flex items-center justify-center glow-primary">
              <Trophy className="w-10 h-10 text-primary" />
            </div>
            <h1 className="font-pixel text-xl sm:text-2xl text-primary text-glow mb-2">
              LEADERBOARD
            </h1>
            <p className="text-muted-foreground">Top snake champions</p>
          </div>

          {/* Mode Filter */}
          <div className="flex justify-center gap-2 mb-8 animate-slide-up" style={{ animationDelay: '0.1s' }}>
            <Button
              variant={filterMode === 'all' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilterMode('all')}
            >
              All
            </Button>
            <Button
              variant={filterMode === 'walls' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilterMode('walls')}
              className="flex items-center gap-2"
            >
              <Shield className="w-4 h-4" />
              Walls
            </Button>
            <Button
              variant={filterMode === 'pass-through' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilterMode('pass-through')}
              className="flex items-center gap-2"
            >
              <Zap className="w-4 h-4" />
              Pass-Through
            </Button>
          </div>

          {/* Leaderboard List */}
          <div className="space-y-3 animate-slide-up" style={{ animationDelay: '0.2s' }}>
            {isLoading ? (
              <div className="text-center py-12">
                <div className="w-12 h-12 mx-auto border-4 border-primary border-t-transparent rounded-full animate-spin" />
                <p className="mt-4 text-muted-foreground">Loading scores...</p>
              </div>
            ) : entries.length === 0 ? (
              <div className="text-center py-12 arcade-border">
                <Trophy className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground">No scores yet. Be the first!</p>
              </div>
            ) : (
              entries.map((entry, index) => (
                <div
                  key={entry.id}
                  className={`flex items-center gap-4 p-4 rounded-lg border-2 transition-all duration-300 hover:scale-[1.02] ${getRankStyle(index + 1)}`}
                  style={{ animationDelay: `${0.2 + index * 0.05}s` }}
                >
                  <div className="flex-shrink-0">
                    {getRankIcon(index + 1)}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-foreground truncate">{entry.username}</p>
                    <div className="flex items-center gap-3 text-sm text-muted-foreground">
                      <span className="flex items-center gap-1">
                        {entry.mode === 'walls' ? (
                          <Shield className="w-3 h-3" />
                        ) : (
                          <Zap className="w-3 h-3" />
                        )}
                        {entry.mode}
                      </span>
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {new Date(entry.date).toLocaleDateString()}
                      </span>
                    </div>
                  </div>

                  <div className="text-right">
                    <p className="font-pixel text-lg text-primary text-glow">{entry.score}</p>
                    <p className="text-xs text-muted-foreground uppercase">points</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Leaderboard;
