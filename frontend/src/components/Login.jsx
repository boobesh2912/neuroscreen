import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Loader2, ShieldCheck } from 'lucide-react';
import { authAPI, getApiErrorMessage } from '../api';

const Login = ({ onLogin }) => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const response = await authAPI.login(formData);
      const { token, user } = response.data;
      onLogin(token, user);
      navigate('/dashboard');
    } catch (err) {
      setError(getApiErrorMessage(err, 'Login failed. Please check your credentials.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-mesh px-4 py-10">
      <div className="mx-auto max-w-5xl overflow-hidden rounded-3xl border border-[var(--line)] bg-[var(--panel)] shadow-soft lg:grid lg:grid-cols-2">
        <aside className="hidden border-r border-[var(--line)] bg-[var(--bg-2)] p-10 lg:block">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-7 w-7 text-[var(--brand-700)]" />
            <span className="font-display text-2xl font-bold text-[var(--ink-900)]">NeuroScreen</span>
          </div>
          <h1 className="mt-6 font-display text-4xl font-bold leading-tight text-[var(--ink-900)]">Welcome back to your screening workspace.</h1>
          <p className="mt-4 text-sm text-[var(--ink-700)]">Securely access dashboard analytics, voice testing, and emergency contact management.</p>
        </aside>

        <section className="p-6 sm:p-10">
          <div className="mb-6 lg:hidden">
            <div className="flex items-center gap-2">
              <ShieldCheck className="h-7 w-7 text-[var(--brand-700)]" />
              <span className="font-display text-2xl font-bold text-[var(--ink-900)]">NeuroScreen</span>
            </div>
          </div>

          <h2 className="font-display text-3xl font-bold text-[var(--ink-900)]">Sign In</h2>
          <p className="mt-2 text-sm text-[var(--ink-700)]">Enter your account credentials.</p>

          {error && <div className="mt-4 rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">{error}</div>}

          <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="username" className="mb-1 block text-sm font-semibold text-[var(--ink-800)]">Username</label>
              <input id="username" name="username" type="text" required value={formData.username} onChange={handleChange} className="w-full rounded-xl border border-[var(--line)] bg-white px-4 py-3 text-sm" />
            </div>
            <div>
              <label htmlFor="password" className="mb-1 block text-sm font-semibold text-[var(--ink-800)]">Password</label>
              <input id="password" name="password" type="password" required value={formData.password} onChange={handleChange} className="w-full rounded-xl border border-[var(--line)] bg-white px-4 py-3 text-sm" />
            </div>
            <button type="submit" disabled={loading} className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-[var(--ink-900)] px-4 py-3 text-sm font-semibold text-white disabled:opacity-60">
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
              {loading ? 'Signing In...' : 'Sign In'}
            </button>
          </form>

          <p className="mt-5 text-sm text-[var(--ink-700)]">
            New to NeuroScreen?{' '}
            <Link to="/register" className="font-semibold text-[var(--brand-700)]">Create account</Link>
          </p>
          <Link to="/" className="mt-2 inline-block text-sm text-[var(--ink-600)] hover:text-[var(--ink-900)]">Back to landing</Link>
        </section>
      </div>
    </div>
  );
};

export default Login;
