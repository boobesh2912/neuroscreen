import { useEffect, useState } from 'react';
import { Download, Loader2, Plus, UserRound, Users, X } from 'lucide-react';
import AppShell from './AppShell';
import { getApiErrorMessage, profileAPI } from '../api';

const panelClass = 'rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5 shadow-soft';

const emptyContact = {
  name: '',
  relationship: '',
  phone: '',
  email: '',
  is_primary: false,
};

const Profile = ({ user, onLogout }) => {
  const [profile, setProfile] = useState(user);
  const [contacts, setContacts] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [loadingContacts, setLoadingContacts] = useState(true);
  const [savingContact, setSavingContact] = useState(false);
  const [contactForm, setContactForm] = useState(emptyContact);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const loadData = async () => {
    setLoadingContacts(true);
    try {
      const [profileRes, contactsRes] = await Promise.all([
        profileAPI.getProfile(),
        profileAPI.getEmergencyContacts(),
      ]);
      if (profileRes?.data?.user) setProfile((p) => ({ ...p, ...profileRes.data.user }));
      setContacts(contactsRes?.data?.contacts || []);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to load profile data. Please refresh.'));
    } finally {
      setLoadingContacts(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const onFormChange = (e) => {
    const { name, value, type, checked } = e.target;
    setContactForm((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const submitContact = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setSavingContact(true);
    try {
      await profileAPI.addEmergencyContact(contactForm);
      setSuccess('Emergency contact added successfully.');
      setContactForm(emptyContact);
      setShowForm(false);
      loadData();
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to add emergency contact.'));
    } finally {
      setSavingContact(false);
    }
  };

  return (
    <AppShell
      user={profile}
      onLogout={onLogout}
      title="Account & Safety Contacts"
      subtitle="Manage patient identity details and emergency support contacts used in clinical escalation workflows."
    >
      <div className="space-y-6">
        {error && <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm font-semibold text-rose-700">{error}</div>}
        {success && <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm font-semibold text-emerald-700">{success}</div>}

        <section className={panelClass}>
          <div className="mb-4 flex items-center gap-2">
            <UserRound className="h-5 w-5 text-[var(--brand-700)]" />
            <h2 className="font-display text-xl font-bold text-[var(--ink-900)]">Personal Information</h2>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-[var(--ink-600)]">Full Name</p>
              <p className="mt-1 rounded-xl bg-[var(--bg-2)] px-4 py-3 text-sm text-[var(--ink-900)]">
                {(profile?.first_name || '').trim()} {(profile?.last_name || '').trim()}
              </p>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-[var(--ink-600)]">Username</p>
              <p className="mt-1 rounded-xl bg-[var(--bg-2)] px-4 py-3 text-sm text-[var(--ink-900)]">{profile?.username || '-'}</p>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-[var(--ink-600)]">Email</p>
              <p className="mt-1 rounded-xl bg-[var(--bg-2)] px-4 py-3 text-sm text-[var(--ink-900)]">{profile?.email || '-'}</p>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-[var(--ink-600)]">Date of Birth</p>
              <p className="mt-1 rounded-xl bg-[var(--bg-2)] px-4 py-3 text-sm text-[var(--ink-900)]">{profile?.date_of_birth || '-'}</p>
            </div>
          </div>
        </section>

        <section className={panelClass}>
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <Users className="h-5 w-5 text-[var(--brand-700)]" />
              <h2 className="font-display text-xl font-bold text-[var(--ink-900)]">Emergency Contacts</h2>
            </div>
            <button
              onClick={() => setShowForm((v) => !v)}
              className="inline-flex items-center gap-2 rounded-full bg-[var(--ink-900)] px-4 py-2 text-sm font-semibold text-white"
            >
              {showForm ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
              {showForm ? 'Close' : 'Add Contact'}
            </button>
          </div>

          {showForm && (
            <form onSubmit={submitContact} className="mb-5 rounded-xl border border-[var(--line)] bg-[var(--bg-2)] p-4">
              <div className="grid gap-3 md:grid-cols-2">
                <input required name="name" value={contactForm.name} onChange={onFormChange} placeholder="Full name" className="rounded-lg border border-[var(--line)] bg-white px-3 py-2 text-sm" />
                <input required name="relationship" value={contactForm.relationship} onChange={onFormChange} placeholder="Relationship" className="rounded-lg border border-[var(--line)] bg-white px-3 py-2 text-sm" />
                <input required name="phone" value={contactForm.phone} onChange={onFormChange} placeholder="Phone" className="rounded-lg border border-[var(--line)] bg-white px-3 py-2 text-sm" />
                <input name="email" value={contactForm.email} onChange={onFormChange} placeholder="Email (optional)" className="rounded-lg border border-[var(--line)] bg-white px-3 py-2 text-sm" />
              </div>
              <label className="mt-3 inline-flex items-center gap-2 text-sm text-[var(--ink-800)]">
                <input type="checkbox" name="is_primary" checked={contactForm.is_primary} onChange={onFormChange} />
                Set as primary contact
              </label>
              <div>
                <button
                  className="mt-3 inline-flex items-center gap-2 rounded-full bg-[var(--brand-700)] px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
                  type="submit"
                  disabled={savingContact}
                >
                  {savingContact ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                  {savingContact ? 'Saving...' : 'Save Contact'}
                </button>
              </div>
            </form>
          )}

          {loadingContacts ? (
            <p className="text-sm text-[var(--ink-700)]">Loading contacts...</p>
          ) : contacts.length === 0 ? (
            <div className="rounded-xl bg-[var(--bg-2)] p-4 text-sm text-[var(--ink-700)]">No emergency contacts yet.</div>
          ) : (
            <div className="space-y-3">
              {contacts.map((contact) => (
                <article key={contact.id} className="rounded-xl border border-[var(--line)] bg-white px-4 py-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div>
                      <p className="font-semibold text-[var(--ink-900)]">{contact.name}</p>
                      <p className="text-xs text-[var(--ink-600)]">{contact.relationship}</p>
                    </div>
                    {contact.is_primary ? (
                      <span className="rounded-full bg-[var(--brand-100)] px-3 py-1 text-xs font-semibold text-[var(--brand-700)]">Primary</span>
                    ) : null}
                  </div>
                  <div className="mt-2 grid gap-2 text-sm text-[var(--ink-800)] sm:grid-cols-2">
                    <p>{contact.phone_number}</p>
                    <p>{contact.email || '-'}</p>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>

        <section className={panelClass}>
          <h2 className="font-display text-xl font-bold text-[var(--ink-900)]">Report Export</h2>
          <p className="mt-2 text-sm text-[var(--ink-700)]">
            Generate a summary PDF of voice screenings and risk trends for clinician review.
          </p>
          <button
            disabled
            className="mt-4 inline-flex items-center gap-2 rounded-full border border-[var(--line)] bg-white px-4 py-2 text-sm font-semibold opacity-70"
            aria-disabled="true"
            title="Export will be enabled in a backend release."
          >
            <Download className="h-4 w-4" />
            Export Report (Coming Soon)
          </button>
        </section>
      </div>
    </AppShell>
  );
};

export default Profile;
