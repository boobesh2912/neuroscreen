import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Loader2, ShieldCheck } from 'lucide-react';
import { authAPI, getApiErrorMessage } from '../api';

const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: '',
    email: '',
    first_name: '',
    last_name: '',
    phone: '',
    dob: '',
    address: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const { confirmPassword, ...registerData } = formData;
      await authAPI.register(registerData);
      navigate('/login', { state: { message: 'Registration successful. Please sign in.' } });
    } catch (err) {
      setError(getApiErrorMessage(err, 'Registration failed. Please try again.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-mesh px-4 py-10">
      <div className="mx-auto max-w-5xl rounded-3xl border border-[var(--line)] bg-[var(--panel)] p-6 shadow-soft sm:p-10">
        <div className="mb-8 flex items-center gap-2">
          <ShieldCheck className="h-7 w-7 text-[var(--brand-700)]" />
          <div>
            <p className="font-display text-2xl font-bold text-[var(--ink-900)]">NeuroScreen</p>
            <p className="text-xs text-[var(--ink-600)]">Create your clinical screening workspace</p>
          </div>
        </div>

        <h1 className="font-display text-3xl font-bold text-[var(--ink-900)]">Create Account</h1>
        <p className="mt-2 text-sm text-[var(--ink-700)]">Set up your identity profile for longitudinal voice health tracking.</p>

        {error && <div className="mt-4 rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">{error}</div>}

        <form onSubmit={handleSubmit} className="mt-6 grid gap-4 sm:grid-cols-2">
          <input name="username" required value={formData.username} onChange={handleChange} placeholder="Username" className="rounded-xl border border-[var(--line)] bg-white px-4 py-3 text-sm" />
          <input name="email" type="email" required value={formData.email} onChange={handleChange} placeholder="Email" className="rounded-xl border border-[var(--line)] bg-white px-4 py-3 text-sm" />
          <input name="password" type="password" required value={formData.password} onChange={handleChange} placeholder="Password" className="rounded-xl border border-[var(--line)] bg-white px-4 py-3 text-sm" />
          <input name="confirmPassword" type="password" required value={formData.confirmPassword} onChange={handleChange} placeholder="Confirm password" className="rounded-xl border border-[var(--line)] bg-white px-4 py-3 text-sm" />
          <input name="first_name" required value={formData.first_name} onChange={handleChange} placeholder="First name" className="rounded-xl border border-[var(--line)] bg-white px-4 py-3 text-sm" />
          <input name="last_name" required value={formData.last_name} onChange={handleChange} placeholder="Last name" className="rounded-xl border border-[var(--line)] bg-white px-4 py-3 text-sm" />
          <input name="phone" value={formData.phone} onChange={handleChange} placeholder="Phone (optional)" className="rounded-xl border border-[var(--line)] bg-white px-4 py-3 text-sm" />
          <input name="dob" type="date" value={formData.dob} onChange={handleChange} className="rounded-xl border border-[var(--line)] bg-white px-4 py-3 text-sm" />
          <textarea name="address" value={formData.address} onChange={handleChange} placeholder="Address (optional)" className="sm:col-span-2 rounded-xl border border-[var(--line)] bg-white px-4 py-3 text-sm" rows="3" />
          <button type="submit" disabled={loading} className="sm:col-span-2 inline-flex items-center justify-center gap-2 rounded-xl bg-[var(--ink-900)] px-4 py-3 text-sm font-semibold text-white disabled:opacity-60">
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
            {loading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        <p className="mt-5 text-sm text-[var(--ink-700)]">
          Already registered? <Link to="/login" className="font-semibold text-[var(--brand-700)]">Sign in</Link>
        </p>
      </div>
    </div>
  );
};

export default Register;
