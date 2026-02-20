import { useState } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { Menu, X, ShieldCheck, LogOut } from 'lucide-react';

const NAV_ITEMS = [
  { to: '/dashboard', label: 'Overview' },
  { to: '/test', label: 'Voice Test' },
  { to: '/bookings', label: 'Consultations' },
  { to: '/learning', label: 'Learning' },
  { to: '/profile', label: 'Account' },
];

const navLinkClass = ({ isActive }) =>
  `rounded-full px-4 py-2 text-sm font-semibold transition ${
    isActive
      ? 'bg-[var(--ink-900)] text-white shadow-soft'
      : 'text-[var(--ink-700)] hover:bg-white/70 hover:text-[var(--ink-900)]'
  }`;

function AppShell({ user, onLogout, title, subtitle, children }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="min-h-screen bg-mesh">
      <header className="sticky top-0 z-50 border-b border-[var(--line)] bg-[var(--panel)]/90 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
          <Link to="/dashboard" className="flex items-center gap-2">
            <ShieldCheck className="h-7 w-7 text-[var(--brand-700)]" />
            <div>
              <p className="font-display text-xl font-bold tracking-tight text-[var(--ink-900)]">NeuroScreen</p>
              <p className="text-xs text-[var(--ink-600)]">Voice Intelligence Platform</p>
            </div>
          </Link>

          <nav className="hidden items-center gap-2 md:flex">
            {NAV_ITEMS.map((item) => (
              <NavLink key={item.to} to={item.to} className={navLinkClass}>
                {item.label}
              </NavLink>
            ))}
          </nav>

          <div className="hidden items-center gap-3 md:flex">
            <div className="text-right">
              <p className="text-sm font-semibold text-[var(--ink-900)]">{user?.first_name || 'User'}</p>
              <p className="text-xs text-[var(--ink-600)]">{user?.email || 'Account'}</p>
            </div>
            <button
              onClick={onLogout}
              className="inline-flex items-center gap-2 rounded-full border border-[var(--line)] bg-white px-4 py-2 text-sm font-semibold text-[var(--ink-800)] hover:border-[var(--ink-300)]"
            >
              <LogOut className="h-4 w-4" />
              Logout
            </button>
          </div>

          <button
            className="inline-flex items-center justify-center rounded-lg border border-[var(--line)] bg-white p-2 md:hidden"
            onClick={() => setOpen((v) => !v)}
            aria-label="Toggle navigation"
          >
            {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>

        {open && (
          <div className="border-t border-[var(--line)] bg-white px-4 py-3 md:hidden">
            <div className="mb-3 rounded-xl bg-[var(--bg-2)] p-3">
              <p className="text-sm font-semibold text-[var(--ink-900)]">{user?.first_name || 'User'}</p>
              <p className="text-xs text-[var(--ink-600)]">{user?.email || 'Account'}</p>
            </div>
            <div className="space-y-2">
              {NAV_ITEMS.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  onClick={() => setOpen(false)}
                  className={({ isActive }) =>
                    `block rounded-lg px-3 py-2 text-sm font-semibold ${
                      isActive ? 'bg-[var(--ink-900)] text-white' : 'text-[var(--ink-800)] bg-[var(--bg-2)]'
                    }`
                  }
                >
                  {item.label}
                </NavLink>
              ))}
              <button
                onClick={onLogout}
                className="mt-2 inline-flex w-full items-center justify-center gap-2 rounded-lg border border-[var(--line)] bg-white px-4 py-2 text-sm font-semibold text-[var(--ink-800)]"
              >
                <LogOut className="h-4 w-4" />
                Logout
              </button>
            </div>
          </div>
        )}
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <section className="mb-8 rounded-3xl border border-[var(--line)] bg-[var(--panel)]/95 p-6 shadow-soft sm:p-8">
          <p className="mb-2 inline-flex rounded-full bg-[var(--brand-100)] px-3 py-1 text-xs font-semibold uppercase tracking-wide text-[var(--brand-700)]">
            Early Detection Workspace
          </p>
          <h1 className="font-display text-3xl font-bold tracking-tight text-[var(--ink-900)] sm:text-4xl">{title}</h1>
          {subtitle && <p className="mt-2 max-w-2xl text-sm text-[var(--ink-700)] sm:text-base">{subtitle}</p>}
        </section>

        {children}
      </main>
    </div>
  );
}

export default AppShell;
