import React, { useEffect, useState } from "react";
import { Terminal, Github } from "lucide-react";

const SECTIONS = [
  { id: "overview", label: "Overview" },
  { id: "architecture", label: "Architecture" },
  { id: "ports", label: "Ports" },
  { id: "fixes", label: "Fixes" },
  { id: "files", label: "Files" },
  { id: "validation", label: "Validation" },
  { id: "quickstart", label: "Quick Start" },
];

export const Nav = () => {
  const [active, setActive] = useState("overview");

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) setActive(e.target.id);
        });
      },
      { rootMargin: "-45% 0px -50% 0px", threshold: 0 }
    );
    SECTIONS.forEach((s) => {
      const el = document.getElementById(s.id);
      if (el) observer.observe(el);
    });
    return () => observer.disconnect();
  }, []);

  const go = (id) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="max-w-[1200px] mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between gap-4">
        <div className="flex items-center gap-2.5 shrink-0">
          <div className="h-8 w-8 rounded-lg grid place-items-center bg-primary/15 border border-primary/25">
            <Terminal className="h-4 w-4 text-primary" />
          </div>
          <div className="leading-tight">
            <div className="text-sm font-semibold tracking-tight">AI Stack Console</div>
            <div className="text-[10px] text-muted-foreground font-mono">openhands + headroom</div>
          </div>
        </div>

        <nav className="hidden md:flex items-center gap-1">
          {SECTIONS.map((s) => (
            <button
              key={s.id}
              data-testid={`nav-link-${s.id}`}
              onClick={() => go(s.id)}
              className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                active === s.id
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:text-foreground hover:bg-muted"
              }`}
            >
              {s.label}
            </button>
          ))}
        </nav>

        <a
          href="https://github.com/All-Hands-AI/OpenHands"
          target="_blank"
          rel="noopener noreferrer"
          data-testid="nav-github-link"
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm border border-border text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
        >
          <Github className="h-4 w-4" />
          <span className="hidden sm:inline">Repo</span>
        </a>
      </div>
    </header>
  );
};

export default Nav;
