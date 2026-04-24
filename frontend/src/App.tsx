export default function App() {
  return (
    <main className="min-h-full px-8 py-12 md:px-16 md:py-20">
      <header className="mb-12 max-w-4xl">
        <p className="font-mono text-xs uppercase tracking-[0.25em] text-calm">
          CVUIA · proof of concept
        </p>
        <h1 className="mt-4 font-sans text-display font-semibold">
          Tremor-adaptive interfaces.
        </h1>
        <p className="mt-6 max-w-xl text-lg leading-relaxed text-ink/75">
          A side-mounted webcam watches the user&rsquo;s hand. The UI scales, spaces out,
          and smooths input in response to hand tremor &mdash; making the interface usable
          when the user&rsquo;s pointer isn&rsquo;t steady.
        </p>
      </header>
      <section className="font-mono text-sm text-calm">
        frontend scaffolding in progress &mdash; number pad + debug panel land in steps
        26&ndash;33.
      </section>
    </main>
  );
}
