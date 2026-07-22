import React from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { CodeBlock } from "./CodeBlock";
import { zipDownloadUrl } from "@/lib/api";
import { Download, ShieldCheck, Network, Ban, ArrowRight } from "lucide-react";
import { toast } from "sonner";

export const Hero = ({ overview }) => {
  const quickStart = overview?.quick_start || "./init.sh && docker compose up -d";

  const onDownload = () => {
    window.location.href = zipDownloadUrl();
    toast.success("Downloading ai-stack.zip");
  };

  const scrollTo = (id) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <section id="overview" className="relative overflow-hidden border-b border-border">
      {/* subtle decorative overlay (<20% viewport) */}
      <div
        aria-hidden
        className="pointer-events-none absolute -top-24 right-0 h-[380px] w-[380px] rounded-full blur-3xl opacity-25"
        style={{ background: "radial-gradient(circle, hsl(var(--primary)) 0%, transparent 60%)" }}
      />
      <div className="max-w-[1200px] mx-auto px-4 sm:px-6 lg:px-8 py-14 sm:py-20 relative">
        <div className="grid lg:grid-cols-12 gap-10 items-center">
          <div className="lg:col-span-7 section-in">
            <div className="inline-flex items-center gap-2 rounded-full border border-primary/25 bg-primary/10 px-3 py-1 text-xs text-primary mb-5">
              <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
              Production-ready Docker Compose stack
            </div>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-semibold tracking-tight">
              OpenHands <span className="text-muted-foreground">+</span>{" "}
              <span className="text-primary">Headroom</span>
            </h1>
            <p className="mt-4 text-base sm:text-lg text-muted-foreground max-w-xl leading-relaxed">
              A two-service AI stack that runs on the first try — with the
              Docker-in-Docker networking and socket-permission traps already
              solved.
            </p>

            <div className="mt-6 flex flex-wrap items-center gap-2">
              <Badge variant="destructive" className="gap-1">
                <Ban className="h-3 w-3" /> Ports 3000 / 4000 blocked
              </Badge>
              <Badge variant="secondary" className="font-mono">OpenHands :5000</Badge>
              <Badge variant="secondary" className="font-mono">Headroom :5001</Badge>
            </div>

            <div className="mt-7 flex flex-wrap items-center gap-3">
              <Button data-testid="hero-download-zip-button" size="lg" onClick={onDownload} className="rounded-xl">
                <Download className="h-4 w-4 mr-2" /> Download stack (.zip)
              </Button>
              <Button
                data-testid="hero-view-files-button"
                size="lg"
                variant="secondary"
                onClick={() => scrollTo("files")}
                className="rounded-xl border border-border"
              >
                Browse files <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </div>

            <div className="mt-6 max-w-xl">
              <div className="text-xs text-muted-foreground mb-1.5 font-mono">get started in one line</div>
              <CodeBlock
                testId="hero-copy-quickstart-button"
                code={quickStart}
                language="bash"
                showLineNumbers={false}
                maxHeight="64px"
              />
            </div>
          </div>

          <div className="lg:col-span-5 section-in">
            <div className="grid gap-3">
              {(overview?.services || []).map((s) => (
                <div key={s.id} className="rounded-xl border border-border bg-card p-4">
                  <div className="flex items-center justify-between">
                    <div className="font-semibold">{s.name}</div>
                    <Badge variant="secondary" className="font-mono text-[11px]">
                      :{s.host_port} &rarr; :{s.container_port}
                    </Badge>
                  </div>
                  <div className="text-sm text-muted-foreground mt-0.5">{s.role}</div>
                  <div className="mt-2 font-mono text-[11px] text-muted-foreground truncate">{s.image}</div>
                </div>
              ))}
              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-xl border border-border bg-card p-4 flex items-start gap-3">
                  <ShieldCheck className="h-5 w-5 text-primary mt-0.5" />
                  <div>
                    <div className="text-sm font-medium">Socket-safe</div>
                    <div className="text-xs text-muted-foreground">group_add, no chmod 666</div>
                  </div>
                </div>
                <div className="rounded-xl border border-border bg-card p-4 flex items-start gap-3">
                  <Network className="h-5 w-5 text-primary mt-0.5" />
                  <div>
                    <div className="text-sm font-medium">DinD-ready</div>
                    <div className="text-xs text-muted-foreground">host-gateway + abs paths</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
