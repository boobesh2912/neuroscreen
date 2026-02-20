import { Link } from 'react-router-dom';
import { AlertTriangle, Home, LogIn } from 'lucide-react';

const NotFound = () => {
  return (
    <div className="min-h-screen bg-mesh px-4 py-12">
      <div className="mx-auto max-w-2xl rounded-3xl border border-[var(--line)] bg-[var(--panel)] p-8 text-center shadow-soft">
        <AlertTriangle className="mx-auto h-12 w-12 text-[var(--brand-700)]" />
        <p className="mt-4 text-xs font-semibold uppercase tracking-wide text-[var(--ink-600)]">NeuroScreen</p>
        <h1 className="mt-2 font-display text-4xl font-bold text-[var(--ink-900)]">Page Not Found</h1>
        <p className="mt-3 text-sm text-[var(--ink-700)]">
          The page you requested is unavailable or has moved. Return to the NeuroScreen home page or sign in.
        </p>
        <div className="mt-6 flex flex-wrap justify-center gap-3">
          <Link
            to="/"
            className="inline-flex items-center gap-2 rounded-full border border-[var(--line)] bg-white px-4 py-2 text-sm font-semibold text-[var(--ink-900)]"
          >
            <Home className="h-4 w-4" />
            Go Home
          </Link>
          <Link
            to="/login"
            className="inline-flex items-center gap-2 rounded-full bg-[var(--ink-900)] px-4 py-2 text-sm font-semibold text-white"
          >
            <LogIn className="h-4 w-4" />
            Sign In
          </Link>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
