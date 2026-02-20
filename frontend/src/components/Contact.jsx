import MarketingLayout from './MarketingLayout';

const Contact = () => (
  <MarketingLayout>
    <section className="mx-auto max-w-4xl px-4 py-14 sm:px-6 lg:px-8">
      <h1 className="font-display text-4xl font-bold">Contact</h1>
      <p className="mt-3 text-[var(--ink-700)]">For product and clinical-support inquiries, reach the team below.</p>
      <div className="mt-8 grid gap-4 sm:grid-cols-2">
        <article className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5 shadow-soft">
          <h3 className="font-display text-xl font-bold">Support</h3>
          <p className="mt-2 text-sm text-[var(--ink-700)]">support@neuroscreen.app</p>
        </article>
        <article className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5 shadow-soft">
          <h3 className="font-display text-xl font-bold">Partnerships</h3>
          <p className="mt-2 text-sm text-[var(--ink-700)]">partnerships@neuroscreen.app</p>
        </article>
      </div>
    </section>
  </MarketingLayout>
);

export default Contact;
