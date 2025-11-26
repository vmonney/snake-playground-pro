import { Navigation } from './Navigation';

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-background scanlines">
      <Navigation />
      <main className="pt-16">
        {children}
      </main>
    </div>
  );
}
