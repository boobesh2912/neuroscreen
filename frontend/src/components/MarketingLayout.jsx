import { Link, useNavigate } from 'react-router-dom';
import { ShieldCheck } from 'lucide-react';

const navItems = [
  { to: '/about', label: 'About' },
  { to: '/how-it-works', label: 'How It Works' },
  { to: '/pricing', label: 'Pricing' },
  { to: '/faq', label: 'FAQ' },
  { to: '/contact', label: 'Contact' },
];

function MarketingLayout({ children }) {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-mesh text-[var(--ink-900)]">
      <header className="sticky top-0 z-40 border-b border-[var(--line)] bg-[var(--panel)]/90 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
          <Link to="/" className="flex items-center gap-2">
            <ShieldCheck className="h-7 w-7 text-[var(--brand-700)]" />
            <span className="font-display text-2xl font-bold">NeuroScreen</span>
          </Link>

          <nav className="hidden items-center gap-4 md:flex">
            {navItems.map((item) => (
              <Link key={item.to} to={item.to} className="text-sm font-semibold text-[var(--ink-700)] hover:text-[var(--ink-900)]">
                {item.label}
              </Link>
            ))}
          </nav>

          <div className="flex gap-2">
            <button onClick={() => navigate('/login')} className="rounded-full border border-[var(--line)] bg-white px-4 py-2 text-sm font-semibold">Sign In</button>
            <button onClick={() => navigate('/register')} className="rounded-full bg-[var(--ink-900)] px-4 py-2 text-sm font-semibold text-white">Start Free</button>
          </div>
        </div>
      </header>

      {children}

      <footer className="border-t border-[var(--line)] bg-[var(--panel)] px-4 py-8 text-[var(--ink-700)]">
        <div className="mx-auto flex max-w-7xl flex-col justify-between gap-4 sm:flex-row sm:items-center">
          <p className="text-sm">NeuroScreen 2026. Voice screening support for early Parkinson's risk detection. By Digital Duo.</p>
          <div className="flex flex-wrap gap-4 text-sm font-semibold">
            <Link to="/about" className="hover:text-[var(--ink-900)]">About</Link>
            <Link to="/how-it-works" className="hover:text-[var(--ink-900)]">How It Works</Link>
            <Link to="/faq" className="hover:text-[var(--ink-900)]">FAQ</Link>
            <Link to="/contact" className="hover:text-[var(--ink-900)]">Contact</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default MarketingLayout;
