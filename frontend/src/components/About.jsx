import MarketingLayout from './MarketingLayout';
import { ShieldCheck, Stethoscope, LineChart, Brain, Clock3, Users, FlaskConical, FileText } from 'lucide-react';

const About = () => (
  <MarketingLayout>
    <section className="mx-auto max-w-6xl px-4 py-14 sm:px-6 lg:px-8">
      <div className="rounded-3xl border border-[var(--line)] bg-[var(--panel)] p-8 shadow-soft sm:p-10">
        <p className="inline-flex items-center rounded-full bg-[var(--brand-100)] px-3 py-1 text-xs font-semibold uppercase tracking-wide text-[var(--brand-700)]">
          Our Story
        </p>
        <h1 className="mt-4 max-w-3xl font-display text-4xl font-bold leading-tight sm:text-5xl">
          Building a calmer first step for neurological screening
        </h1>
        <p className="mt-4 max-w-3xl text-base text-[var(--ink-700)] sm:text-lg">
          NeuroScreen helps people run structured voice checks at home and share trends with clinicians. We focus on early risk indication,
          repeatability, and clarity so users can act sooner with better information.
        </p>
      </div>

      <div className="mt-8 grid gap-4 md:grid-cols-3">
        <article className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5 shadow-soft">
          <ShieldCheck className="h-5 w-5 text-[var(--brand-700)]" />
          <h2 className="mt-3 font-display text-xl font-bold">Mission</h2>
          <p className="mt-2 text-sm text-[var(--ink-700)]">Make neurological risk screening accessible, repeatable, and understandable.</p>
        </article>
        <article className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5 shadow-soft">
          <Stethoscope className="h-5 w-5 text-[var(--brand-700)]" />
          <h2 className="mt-3 font-display text-xl font-bold">Clinical Intent</h2>
          <p className="mt-2 text-sm text-[var(--ink-700)]">Support clinician conversations with objective trend summaries from routine tests.</p>
        </article>
        <article className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5 shadow-soft">
          <LineChart className="h-5 w-5 text-[var(--brand-700)]" />
          <h2 className="mt-3 font-display text-xl font-bold">Model Approach</h2>
          <p className="mt-2 text-sm text-[var(--ink-700)]">Voice biomarkers + machine learning scoring + longitudinal tracking and alerts.</p>
        </article>
      </div>

      <div className="mt-10 grid gap-6 lg:grid-cols-2">
        <section className="rounded-2xl border border-[var(--line)] bg-white p-6">
          <h2 className="font-display text-2xl font-bold">How Detection Works</h2>
          <div className="mt-5 space-y-4 text-sm text-[var(--ink-700)]">
            <div className="flex items-start gap-3">
              <span className="mt-1 inline-block h-2.5 w-2.5 rounded-full bg-[var(--brand-700)]" />
              <p>Record a guided voice sample (sustained vowel or vowel-sequence) in a quiet environment.</p>
            </div>
            <div className="flex items-start gap-3">
              <span className="mt-1 inline-block h-2.5 w-2.5 rounded-full bg-[var(--brand-700)]" />
              <p>Extract acoustic biomarkers including F0, jitter, shimmer, HNR, MFCCs, formants, pauses, and tremor bands.</p>
            </div>
            <div className="flex items-start gap-3">
              <span className="mt-1 inline-block h-2.5 w-2.5 rounded-full bg-[var(--brand-700)]" />
              <p>Compute disease likelihood scores across Parkinson&apos;s, Alzheimer&apos;s, ALS, MS, and Stroke profiles.</p>
            </div>
            <div className="flex items-start gap-3">
              <span className="mt-1 inline-block h-2.5 w-2.5 rounded-full bg-[var(--brand-700)]" />
              <p>Return confidence-ranked outputs, risk level, and specialist guidance for follow-up care.</p>
            </div>
          </div>
        </section>

        <section className="rounded-2xl border border-[var(--line)] bg-white p-6">
          <h2 className="font-display text-2xl font-bold">Design Principles</h2>
          <div className="mt-5 grid gap-4">
            <article className="rounded-xl bg-[var(--bg-1)] p-4">
              <div className="flex items-center gap-2">
                <Brain className="h-4 w-4 text-[var(--brand-700)]" />
                <h3 className="font-display text-lg font-bold">Signal Over Noise</h3>
              </div>
              <p className="mt-1 text-sm text-[var(--ink-700)]">Every screen and chart should help users make one clear decision.</p>
            </article>
            <article className="rounded-xl bg-[var(--bg-1)] p-4">
              <div className="flex items-center gap-2">
                <Clock3 className="h-4 w-4 text-[var(--brand-700)]" />
                <h3 className="font-display text-lg font-bold">Consistency First</h3>
              </div>
              <p className="mt-1 text-sm text-[var(--ink-700)]">Short recurring tests are more valuable than one-off recordings.</p>
            </article>
            <article className="rounded-xl bg-[var(--bg-1)] p-4">
              <div className="flex items-center gap-2">
                <Users className="h-4 w-4 text-[var(--brand-700)]" />
                <h3 className="font-display text-lg font-bold">Human in the Loop</h3>
              </div>
              <p className="mt-1 text-sm text-[var(--ink-700)]">Predictions are screening signals, not medical diagnosis.</p>
            </article>
          </div>
        </section>
      </div>

      <div className="mt-10 grid gap-6 lg:grid-cols-2">
        <section className="rounded-2xl border border-[var(--line)] bg-white p-6">
          <div className="flex items-center gap-2">
            <FlaskConical className="h-5 w-5 text-[var(--brand-700)]" />
            <h2 className="font-display text-2xl font-bold">Clinical Basis</h2>
          </div>
          <p className="mt-3 text-sm text-[var(--ink-700)]">
            The detection flow follows clinically used voice markers from neurological speech research, with screening-oriented thresholds and
            trend tracking. It is intended for early risk indication and clinician discussion support.
          </p>
        </section>

        <section className="rounded-2xl border border-[var(--line)] bg-white p-6">
          <div className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-[var(--brand-700)]" />
            <h2 className="font-display text-2xl font-bold">Selected Citations</h2>
          </div>
          <ul className="mt-3 space-y-2 text-sm text-[var(--ink-700)]">
            <li>Little et al. (2009) - Dysphonia features for Parkinson&apos;s telemonitoring.</li>
            <li>Toth et al. (2018) - Speech fluency markers in Alzheimer&apos;s disease.</li>
            <li>Green et al. (2013) - Bulbar speech assessment characteristics in ALS.</li>
            <li>Hartelius et al. (2000) - Speech and swallowing patterns in MS.</li>
            <li>Duffy (2013) - Motor speech disorder framework for stroke/aphasia.</li>
          </ul>
          <p className="mt-3 text-xs text-[var(--ink-600)]">
            Full reference summary is available in project docs: <span className="font-semibold">MULTI_DISEASE_DETECTION.md</span>.
          </p>
        </section>
      </div>

      <div className="mt-10 rounded-2xl border border-[var(--line)] bg-[var(--brand-100)]/55 p-6 sm:p-8">
        <h2 className="font-display text-2xl font-bold">Clinical Disclaimer</h2>
        <p className="mt-2 text-sm text-[var(--ink-700)] sm:text-base">
          NeuroScreen is a screening support system. It does not diagnose disease, replace licensed medical advice, or substitute for professional
          neurological evaluation.
        </p>
      </div>
    </section>
  </MarketingLayout>
);

export default About;
