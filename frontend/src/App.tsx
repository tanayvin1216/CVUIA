import { TremorProvider, useTremor } from "@/context/TremorContext";

export default function App() {
  return (
    <TremorProvider>
      <AppShell />
    </TremorProvider>
  );
}

function AppShell() {
  const { connected, level, hand } = useTremor();
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
          and smooths input in response to hand tremor.
        </p>
      </header>
      <section className="font-mono text-sm text-calm">
        ws: {connected ? "connected" : "…disconnected"} &middot; level: {level.toFixed(2)}{" "}
        &middot; hand: {hand ?? "none"}
      </section>
    </main>
  );
}
