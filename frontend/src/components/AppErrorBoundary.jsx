import React from 'react';
import { AlertTriangle, RefreshCcw } from 'lucide-react';

class AppErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch() {
    // Intentionally empty: keep UI fallback user-friendly without exposing internals.
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-mesh px-4 py-12">
          <div className="mx-auto max-w-2xl rounded-3xl border border-[var(--line)] bg-[var(--panel)] p-8 text-center shadow-soft">
            <AlertTriangle className="mx-auto h-12 w-12 text-rose-600" />
            <h1 className="mt-4 font-display text-3xl font-bold text-[var(--ink-900)]">
              Something went wrong
            </h1>
            <p className="mt-2 text-sm text-[var(--ink-700)]">
              NeuroScreen encountered an unexpected error. Refresh the page and try again.
            </p>
            <button
              type="button"
              onClick={() => window.location.reload()}
              className="mt-6 inline-flex items-center gap-2 rounded-full bg-[var(--ink-900)] px-5 py-2 text-sm font-semibold text-white"
            >
              <RefreshCcw className="h-4 w-4" />
              Reload App
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default AppErrorBoundary;
