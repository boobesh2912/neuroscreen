import { Activity, BrainCircuit, Stethoscope, Mic } from 'lucide-react';
import MarketingLayout from './MarketingLayout';

const Landing = () => {
  return (
    <MarketingLayout>
      <section className="mx-auto grid max-w-7xl gap-8 px-4 pb-14 pt-12 sm:px-6 lg:grid-cols-2 lg:items-center lg:px-8">
        <div>
          <span className="inline-flex items-center gap-2 rounded-full bg-[var(--brand-100)] px-3 py-1 text-xs font-semibold uppercase tracking-wide text-[var(--brand-700)]">
            Preventive Neuro Screening
          </span>
          <h1 className="mt-5 font-display text-4xl font-bold tracking-tight text-[var(--ink-900)] sm:text-5xl lg:text-6xl">
            Voice-based early signal detection for Parkinson's risk.
          </h1>
          <p className="mt-5 max-w-xl text-base text-[var(--ink-700)] sm:text-lg">
            Secure account, guided voice recording, interpretable biomarkers, and longitudinal tracking in one micro-SaaS workflow.
          </p>
        </div>

        <div className="rounded-3xl border border-[var(--line)] bg-[var(--panel)] p-6 shadow-soft sm:p-8">
          <div className="grid gap-4 sm:grid-cols-2">
            <article className="rounded-2xl bg-[var(--bg-2)] p-4">
              <Mic className="h-5 w-5 text-[var(--brand-700)]" />
              <h3 className="mt-3 font-display text-lg font-bold">30s Voice Capture</h3>
              <p className="mt-1 text-sm text-[var(--ink-700)]">Record or upload audio in browser.</p>
            </article>
            <article className="rounded-2xl bg-[var(--bg-2)] p-4">
              <BrainCircuit className="h-5 w-5 text-[var(--brand-700)]" />
              <h3 className="mt-3 font-display text-lg font-bold">AI Inference</h3>
              <p className="mt-1 text-sm text-[var(--ink-700)]">Risk score, confidence, and feature metrics.</p>
            </article>
            <article className="rounded-2xl bg-[var(--bg-2)] p-4">
              <Activity className="h-5 w-5 text-[var(--brand-700)]" />
              <h3 className="mt-3 font-display text-lg font-bold">History Tracking</h3>
              <p className="mt-1 text-sm text-[var(--ink-700)]">Trend line for repeat screenings.</p>
            </article>
            <article className="rounded-2xl bg-[var(--bg-2)] p-4">
              <Stethoscope className="h-5 w-5 text-[var(--brand-700)]" />
              <h3 className="mt-3 font-display text-lg font-bold">Clinical Handoff</h3>
              <p className="mt-1 text-sm text-[var(--ink-700)]">Action-focused recommendations.</p>
            </article>
          </div>
        </div>
      </section>

      <section className="mx-auto grid max-w-7xl gap-4 px-4 pb-16 sm:grid-cols-3 sm:px-6 lg:px-8">
        {[
          ['Guided Capture', 'Standardized audio collection flow'],
          ['Risk Tracking', 'Longitudinal trend visibility'],
          ['Clinical Handoff', 'Specialist-ready summary outputs'],
        ].map(([title, label]) => (
          <div key={title} className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5 shadow-soft">
            <p className="font-display text-2xl font-bold">{title}</p>
            <p className="mt-1 text-sm text-[var(--ink-700)]">{label}</p>
          </div>
        ))}
      </section>
    </MarketingLayout>
  );
};

export default Landing;
