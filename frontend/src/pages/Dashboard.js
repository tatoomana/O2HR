import React, { useEffect, useState } from "react";
import Nav from "@/components/dashboard/Nav";
import Hero from "@/components/dashboard/Hero";
import Architecture from "@/components/dashboard/Architecture";
import Ports from "@/components/dashboard/Ports";
import Fixes from "@/components/dashboard/Fixes";
import Files from "@/components/dashboard/Files";
import Validation from "@/components/dashboard/Validation";
import QuickStart from "@/components/dashboard/QuickStart";
import { getOverview } from "@/lib/api";
import { Terminal } from "lucide-react";

const Section = ({ id, eyebrow, title, description, children }) => (
  <section id={id} className="scroll-mt-20 py-10 sm:py-14 section-in">
    <div className="mb-6">
      {eyebrow && (
        <div className="text-xs font-mono uppercase tracking-wider text-primary mb-2">{eyebrow}</div>
      )}
      <h2 className="text-xl sm:text-2xl font-semibold tracking-tight">{title}</h2>
      {description && <p className="text-sm text-muted-foreground mt-1.5 max-w-2xl">{description}</p>}
    </div>
    {children}
  </section>
);

export default function Dashboard() {
  const [overview, setOverview] = useState(null);

  useEffect(() => {
    getOverview().then(setOverview).catch(() => {});
  }, []);

  return (
    <div className="min-h-screen">
      <Nav />
      <Hero overview={overview} />

      <main className="max-w-[1200px] mx-auto px-4 sm:px-6 lg:px-8">
        <Section
          id="architecture"
          eyebrow="How it fits together"
          title="Architecture"
          description="Two services on a shared bridge network. OpenHands talks to the host Docker daemon to spawn its sandbox as a sibling container — which is exactly why the workspace must be an absolute host path."
        >
          <Architecture />
        </Section>

        <Section
          id="ports"
          eyebrow="Networking constraints"
          title="Port mapping"
          description="Host ports 3000 and 4000 are strictly avoided. The UIs are exposed on 5000 and 5001."
        >
          <Ports />
        </Section>

        <Section
          id="fixes"
          eyebrow="Why it works first try"
          title="Fixes applied"
          description="The two failure modes that break this stack — solved and documented."
        >
          <Fixes fixes={overview?.fixes || []} />
        </Section>

        <Section
          id="files"
          eyebrow="The deliverables"
          title="Generated files"
          description="Browse, copy, or download every file in the bundle. Grab everything at once with the Download button in the header."
        >
          <Files />
        </Section>

        <Section
          id="validation"
          eyebrow="Proof, not promises"
          title="Validation"
          description="Every invariant and both reliability fixes are checked automatically against the actual compose file."
        >
          <Validation />
        </Section>

        <Section
          id="quickstart"
          eyebrow="Ship it"
          title="Quick start"
          description="Three commands from clone to running stack."
        >
          <QuickStart />
        </Section>
      </main>

      <footer className="border-t border-border mt-8">
        <div className="max-w-[1200px] mx-auto px-4 sm:px-6 lg:px-8 py-8 flex items-center justify-between gap-4 flex-wrap">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Terminal className="h-4 w-4 text-primary" />
            AI Stack Console — OpenHands + Headroom
          </div>
          <div className="text-xs text-muted-foreground font-mono">restart: unless-stopped · no deprecated compose syntax</div>
        </div>
      </footer>
    </div>
  );
}
