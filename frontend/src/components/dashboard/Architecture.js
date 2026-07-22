import React from "react";
import { Card } from "@/components/ui/card";

const T = ({ x, y, children, size = 12, mono, anchor = "start", fill = "foreground", weight = 400, opacity = 1 }) => (
  <text
    x={x}
    y={y}
    fontSize={size}
    textAnchor={anchor}
    fontWeight={weight}
    opacity={opacity}
    style={{
      fill: fill === "foreground" ? "hsl(var(--foreground))" : fill === "muted" ? "hsl(var(--muted-foreground))" : fill === "primary" ? "hsl(var(--primary))" : fill,
      fontFamily: mono ? "'JetBrains Mono', monospace" : "'IBM Plex Sans', sans-serif",
    }}
  >
    {children}
  </text>
);

export const Architecture = () => {
  const border = "hsl(var(--border))";
  const card = "hsl(var(--card))";
  const primary = "hsl(var(--primary))";
  const panel2 = "var(--panel-2)";

  return (
    <Card className="overflow-hidden border-border bg-card">
      <div className="thin-scroll overflow-x-auto p-2 sm:p-4">
        <svg viewBox="0 0 1000 380" className="w-full min-w-[720px]" style={{ height: "auto" }} role="img" aria-label="Architecture diagram">
          <defs>
            <marker id="arrow" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto" markerUnits="strokeWidth">
              <path d="M0,0 L7,3 L0,6 Z" fill={primary} />
            </marker>
            <marker id="arrowMuted" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto" markerUnits="strokeWidth">
              <path d="M0,0 L7,3 L0,6 Z" fill="hsl(var(--muted-foreground))" />
            </marker>
          </defs>

          {/* Host boundary */}
          <rect x="16" y="44" width="968" height="320" rx="16" fill="none" stroke={border} strokeDasharray="6 6" />
          <T x={32} y={34} size={12} mono fill="muted">HOST · Docker Engine</T>

          {/* Host port ingress */}
          <T x={220} y={30} size={12} mono fill="primary" anchor="middle">host :5000</T>
          <line x1="220" y1="40" x2="220" y2="90" stroke={primary} strokeWidth="2" markerEnd="url(#arrow)" />
          <T x={780} y={30} size={12} mono fill="primary" anchor="middle">host :5001</T>
          <line x1="780" y1="40" x2="780" y2="90" stroke={primary} strokeWidth="2" markerEnd="url(#arrow)" />

          {/* OpenHands node */}
          <rect x="70" y="90" width="300" height="110" rx="12" fill={card} stroke={border} />
          <T x={92} y={122} size={17} weight={600}>OpenHands</T>
          <T x={92} y={144} size={12} fill="muted">Autonomous AI software engineer</T>
          <rect x="92" y="158" width="70" height="24" rx="6" fill="none" stroke={primary} />
          <T x={127} y={174} size={12} mono fill="primary" anchor="middle">:3000</T>
          <T x={176} y={174} size={11} mono fill="muted">container port</T>

          {/* Headroom node */}
          <rect x="630" y="90" width="300" height="110" rx="12" fill={card} stroke={border} />
          <T x={652} y={122} size={17} weight={600}>Headroom</T>
          <T x={652} y={144} size={12} fill="muted">LLM proxy · caching &amp; cost</T>
          <rect x="652" y="158" width="70" height="24" rx="6" fill="none" stroke={primary} />
          <T x={687} y={174} size={12} mono fill="primary" anchor="middle">:8787</T>
          <T x={736} y={174} size={11} mono fill="muted">container port</T>

          {/* Network pill */}
          <rect x="430" y="122" width="140" height="46" rx="23" fill="hsl(var(--primary) / 0.12)" stroke={primary} />
          <T x={500} y={143} size={12} mono fill="primary" anchor="middle" weight={600}>ai-stack</T>
          <T x={500} y={158} size={11} mono fill="primary" anchor="middle">-network</T>
          <line x1="370" y1="145" x2="426" y2="145" stroke={primary} strokeWidth="2" markerEnd="url(#arrow)" />
          <line x1="570" y1="145" x2="626" y2="145" stroke={primary} strokeWidth="2" markerEnd="url(#arrow)" />

          {/* Docker socket */}
          <rect x="70" y="252" width="190" height="50" rx="10" fill={panel2} stroke={border} />
          <T x={165} y={273} size={11} mono anchor="middle" fill="muted">/var/run</T>
          <T x={165} y={289} size={12} mono anchor="middle">docker.sock</T>
          <line x1="150" y1="200" x2="150" y2="250" stroke="hsl(var(--muted-foreground))" strokeWidth="1.5" markerEnd="url(#arrowMuted)" />
          <T x={160} y={228} size={11} fill="muted">mounts</T>

          {/* Sandbox sibling */}
          <rect x="300" y="252" width="200" height="50" rx="10" fill="none" stroke={primary} strokeDasharray="5 4" />
          <T x={400} y={273} size={12} anchor="middle" weight={600}>Sandbox</T>
          <T x={400} y={289} size={11} mono anchor="middle" fill="muted">sibling container</T>
          <line x1="260" y1="277" x2="296" y2="277" stroke={primary} strokeWidth="2" strokeDasharray="5 4" markerEnd="url(#arrow)" />
          <T x={278} y={244} size={11} fill="primary" anchor="middle">spawns</T>

          {/* Workspace */}
          <rect x="540" y="252" width="250" height="50" rx="10" fill={panel2} stroke={border} />
          <T x={665} y={273} size={11} mono anchor="middle" fill="muted">./workspace (abs host path)</T>
          <T x={665} y={289} size={11} mono anchor="middle">→ /opt/workspace_base</T>
          <line x1="500" y1="277" x2="536" y2="277" stroke="hsl(var(--muted-foreground))" strokeWidth="1.5" markerEnd="url(#arrowMuted)" />

          {/* Headroom volume */}
          <rect x="812" y="252" width="120" height="50" rx="10" fill={panel2} stroke={border} />
          <T x={872} y={273} size={11} mono anchor="middle" fill="muted">volume</T>
          <T x={872} y={289} size={11} mono anchor="middle">headroom-data</T>
          <line x1="820" y1="200" x2="860" y2="250" stroke="hsl(var(--muted-foreground))" strokeWidth="1.5" markerEnd="url(#arrowMuted)" />
        </svg>
      </div>
    </Card>
  );
};

export default Architecture;
