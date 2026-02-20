import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, Clock3, AlertTriangle, Mic, CheckCircle2, RefreshCcw } from 'lucide-react';
import AppShell from './AppShell';
import { dashboardAPI, getApiErrorMessage } from '../api';

function riskMeta(score) {
  if (score < 30) return { label: 'Low', tone: 'text-emerald-700', bg: 'bg-emerald-500' };
  if (score < 60) return { label: 'Medium', tone: 'text-amber-700', bg: 'bg-amber-500' };
  return { label: 'High', tone: 'text-rose-700', bg: 'bg-rose-500' };
}

const cardClass = 'rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5 shadow-soft';

const Dashboard = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchDashboard = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await dashboardAPI.getDashboard();
      setDashboardData(response.data);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Unable to load dashboard data. Please try again.'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  const chartData = useMemo(() => {
    const history = dashboardData?.test_history || [];
    return history.slice(0, 7).reverse();
  }, [dashboardData]);

  const stats = dashboardData?.statistics;
  const latestRisk = stats?.latest_risk_score ?? 0;
  const latestRiskMeta = riskMeta(latestRisk);

  return (
    <AppShell
      user={user}
      onLogout={onLogout}
      title="Clinical Signal Overview"
      subtitle="Track progression trends, review prior assessments, and launch a fresh voice screening in one place."
    >
      {loading ? (
        <div className="grid gap-4 md:grid-cols-3">
          {[...Array(6)].map((_, idx) => (
            <div key={idx} className={`${cardClass} h-32 animate-pulse bg-[var(--bg-2)]`} />
          ))}
        </div>
      ) : error ? (
        <div className="rounded-2xl border border-rose-200 bg-rose-50 p-6">
          <p className="font-semibold text-rose-700">{error}</p>
          <button
            onClick={fetchDashboard}
            className="mt-4 inline-flex items-center gap-2 rounded-full bg-rose-600 px-4 py-2 text-sm font-semibold text-white"
          >
            <RefreshCcw className="h-4 w-4" />
            Retry
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          <section className="grid gap-4 md:grid-cols-3">
            <article className={cardClass}>
              <p className="text-xs font-semibold uppercase tracking-wide text-[var(--ink-600)]">Latest Risk</p>
              <div className="mt-3 flex items-end justify-between">
                <p className="font-display text-4xl font-bold text-[var(--ink-900)]">{latestRisk}%</p>
                <Activity className="h-6 w-6 text-[var(--brand-700)]" />
              </div>
              <p className={`mt-2 text-sm font-semibold ${latestRiskMeta.tone}`}>{latestRiskMeta.label} Concern</p>
            </article>

            <article className={cardClass}>
              <p className="text-xs font-semibold uppercase tracking-wide text-[var(--ink-600)]">Total Tests</p>
              <div className="mt-3 flex items-end justify-between">
                <p className="font-display text-4xl font-bold text-[var(--ink-900)]">{stats?.total_tests ?? 0}</p>
                <Clock3 className="h-6 w-6 text-[var(--ink-700)]" />
              </div>
              <p className="mt-2 text-sm text-[var(--ink-700)]">Lifetime completed assessments</p>
            </article>

            <article className={cardClass}>
              <p className="text-xs font-semibold uppercase tracking-wide text-[var(--ink-600)]">Model Confidence</p>
              <div className="mt-3 flex items-end justify-between">
                <p className="font-display text-4xl font-bold text-[var(--ink-900)]">{stats?.avg_confidence ?? 0}%</p>
                <CheckCircle2 className="h-6 w-6 text-[var(--brand-700)]" />
              </div>
              <p className="mt-2 text-sm text-[var(--ink-700)]">Average certainty across all analyses</p>
            </article>
          </section>

          <section className={`${cardClass} overflow-hidden`}>
            <div className="mb-4 flex items-center justify-between">
              <h2 className="font-display text-xl font-bold text-[var(--ink-900)]">Risk Trend</h2>
              <button
                onClick={() => navigate('/test')}
                className="inline-flex items-center gap-2 rounded-full bg-[var(--ink-900)] px-4 py-2 text-sm font-semibold text-white"
              >
                <Mic className="h-4 w-4" />
                New Voice Test
              </button>
            </div>

            {chartData.length === 0 ? (
              <div className="rounded-xl bg-[var(--bg-2)] p-8 text-center text-[var(--ink-700)]">
                No tests yet. Run your first voice screening to populate this chart.
              </div>
            ) : (
              <div className="grid grid-cols-7 gap-3">
                {chartData.map((item) => {
                  const meta = riskMeta(item.risk_score);
                  return (
                    <div key={item.id} className="flex flex-col items-center gap-2">
                      <div className="relative h-44 w-full rounded-xl bg-[var(--bg-2)] p-2">
                        <div className={`absolute bottom-2 left-2 right-2 rounded-lg ${meta.bg}`} style={{ height: `${Math.max(item.risk_score, 8)}%` }} />
                      </div>
                      <p className="text-xs font-semibold text-[var(--ink-700)]">{item.risk_score}%</p>
                      <p className="text-[11px] text-[var(--ink-600)]">
                        {new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                      </p>
                    </div>
                  );
                })}
              </div>
            )}
          </section>

          <section className={cardClass}>
            <h2 className="mb-4 font-display text-xl font-bold text-[var(--ink-900)]">Assessment History</h2>
            {dashboardData?.test_history?.length ? (
              <div className="space-y-3">
                {dashboardData.test_history.map((test) => {
                  const meta = riskMeta(test.risk_score);
                  return (
                    <div key={test.id} className="flex items-center justify-between rounded-xl border border-[var(--line)] bg-white px-4 py-3">
                      <div>
                        <p className="font-semibold text-[var(--ink-900)]">
                          {new Date(test.date).toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                          })}
                        </p>
                        <p className="text-xs text-[var(--ink-600)]">Confidence: {Math.round(test.confidence * 100)}%</p>
                      </div>
                      <div className="text-right">
                        <p className="font-display text-2xl font-bold text-[var(--ink-900)]">{test.risk_score}%</p>
                        <p className={`text-xs font-semibold ${meta.tone}`}>{meta.label} Concern</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="rounded-xl bg-[var(--bg-2)] p-6 text-sm text-[var(--ink-700)]">
                You do not have prior tests. Start with "New Voice Test" to begin tracking.
              </div>
            )}

            {latestRisk >= 60 && (
              <div className="mt-4 flex items-start gap-3 rounded-xl border border-amber-300 bg-amber-50 p-4 text-sm text-amber-800">
                <AlertTriangle className="mt-0.5 h-4 w-4" />
                Recent risk is elevated. Please follow up with a clinician for formal evaluation.
              </div>
            )}
          </section>
        </div>
      )}
    </AppShell>
  );
};

export default Dashboard;
