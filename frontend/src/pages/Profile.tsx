import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layout } from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import { userApi } from '@/services/api';
import { Button } from '@/components/ui/button';
import { User, Trophy, Gamepad2, Calendar, Award } from 'lucide-react';

interface UserStats {
  highScore: number;
  gamesPlayed: number;
  rank: number;
}

const Profile = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState<UserStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    const fetchStats = async () => {
      if (user) {
        try {
          const userStats = await userApi.getStats(user.id);
          setStats(userStats);
        } catch (error) {
          console.error('Failed to fetch stats:', error);
        }
      }
      setIsLoading(false);
    };

    fetchStats();
  }, [isAuthenticated, user, navigate]);

  if (!user) return null;

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-md mx-auto">
          {/* Profile Header */}
          <div className="text-center mb-8 animate-slide-up">
            <div className="w-24 h-24 mx-auto mb-4 rounded-2xl bg-primary/20 flex items-center justify-center glow-primary">
              <User className="w-12 h-12 text-primary" />
            </div>
            <h1 className="font-pixel text-xl text-primary text-glow mb-2">
              {user.username}
            </h1>
            <p className="text-muted-foreground">{user.email}</p>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-2 gap-4 mb-8 animate-slide-up" style={{ animationDelay: '0.1s' }}>
            <div className="arcade-border p-4 text-center">
              <Trophy className="w-8 h-8 mx-auto mb-2 text-yellow-500" />
              <p className="font-pixel text-lg text-primary text-glow">
                {isLoading ? '...' : stats?.highScore || 0}
              </p>
              <p className="text-xs text-muted-foreground uppercase">High Score</p>
            </div>

            <div className="arcade-border p-4 text-center">
              <Award className="w-8 h-8 mx-auto mb-2 text-accent" />
              <p className="font-pixel text-lg text-primary text-glow">
                #{isLoading ? '...' : stats?.rank || '-'}
              </p>
              <p className="text-xs text-muted-foreground uppercase">Rank</p>
            </div>

            <div className="arcade-border p-4 text-center">
              <Gamepad2 className="w-8 h-8 mx-auto mb-2 text-primary" />
              <p className="font-pixel text-lg text-primary text-glow">
                {isLoading ? '...' : stats?.gamesPlayed || 0}
              </p>
              <p className="text-xs text-muted-foreground uppercase">Games</p>
            </div>

            <div className="arcade-border p-4 text-center">
              <Calendar className="w-8 h-8 mx-auto mb-2 text-muted-foreground" />
              <p className="font-pixel text-sm text-primary text-glow">
                {new Date(user.createdAt).toLocaleDateString('en-US', { month: 'short', year: '2-digit' })}
              </p>
              <p className="text-xs text-muted-foreground uppercase">Joined</p>
            </div>
          </div>

          {/* Actions */}
          <div className="space-y-4 animate-slide-up" style={{ animationDelay: '0.2s' }}>
            <Button
              variant="arcade"
              className="w-full"
              onClick={() => navigate('/')}
            >
              <Gamepad2 className="w-4 h-4" />
              Play Now
            </Button>

            <Button
              variant="outline"
              className="w-full"
              onClick={() => navigate('/leaderboard')}
            >
              <Trophy className="w-4 h-4" />
              View Leaderboard
            </Button>

            <Button
              variant="ghost"
              className="w-full text-destructive hover:text-destructive"
              onClick={() => {
                logout();
                navigate('/');
              }}
            >
              Logout
            </Button>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Profile;
