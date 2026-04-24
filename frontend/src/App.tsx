import { NumberPad } from "@/components/NumberPad";
import { SmoothTracker } from "@/components/SmoothTracker";
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
          smooths input, and debounces clicks in response to hand tremor.
        </p>
      </header>

      <section className="grid gap-12 lg:grid-cols-[auto_1fr_auto]">
        <NumberPad />
        <SmoothTracker />
        <aside className="space-y-2 font-mono text-sm text-calm">
          <div>ws · {connected ? "connected" : "disconnected"}</div>
          <div>level · {level.toFixed(2)}</div>
          <div>hand · {hand ?? "none"}</div>
          <p className="max-w-xs pt-4 text-ink/50">
            Debug panel with live meter, frequency, and manual override slider lands
            in the next three commits.
          </p>
        </aside>
      </section>
    </main>
  );
}
