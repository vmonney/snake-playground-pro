import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Layout } from '@/components/Layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';
import { LogIn, Mail, Lock, ArrowRight } from 'lucide-react';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !password) {
      toast.error('Please fill in all fields');
      return;
    }

    setIsLoading(true);
    try {
      await login(email, password);
      toast.success('Welcome back!');
      navigate('/');
    } catch (error) {
      toast.error('Invalid credentials. Try: snake@test.com');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Layout>
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-md mx-auto">
          <div className="text-center mb-8 animate-slide-up">
            <div className="w-20 h-20 mx-auto mb-4 rounded-2xl bg-primary/20 flex items-center justify-center glow-primary">
              <LogIn className="w-10 h-10 text-primary" />
            </div>
            <h1 className="font-pixel text-xl text-primary text-glow mb-2">LOGIN</h1>
            <p className="text-muted-foreground">Enter the arcade</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6 animate-slide-up" style={{ animationDelay: '0.1s' }}>
            <div className="arcade-border p-6 space-y-4">
              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium text-foreground flex items-center gap-2">
                  <Mail className="w-4 h-4 text-primary" />
                  Email
                </label>
                <Input
                  id="email"
                  type="email"
                  placeholder="snake@test.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  autoComplete="email"
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="password" className="text-sm font-medium text-foreground flex items-center gap-2">
                  <Lock className="w-4 h-4 text-primary" />
                  Password
                </label>
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="current-password"
                />
              </div>

              <Button
                type="submit"
                variant="arcade"
                className="w-full"
                disabled={isLoading}
              >
                {isLoading ? 'Logging in...' : 'Login'}
                <ArrowRight className="w-4 h-4" />
              </Button>
            </div>
          </form>

          <div className="text-center mt-6 animate-slide-up" style={{ animationDelay: '0.2s' }}>
            <p className="text-muted-foreground">
              New player?{' '}
              <Link to="/signup" className="text-primary hover:text-primary/80 transition-colors">
                Create account
              </Link>
            </p>
          </div>

          <div className="mt-8 p-4 bg-secondary/50 rounded-lg text-sm text-muted-foreground animate-slide-up" style={{ animationDelay: '0.3s' }}>
            <p className="font-medium text-foreground mb-2">Demo Credentials:</p>
            <p>Email: snake@test.com</p>
            <p>Password: any 4+ characters</p>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Login;
