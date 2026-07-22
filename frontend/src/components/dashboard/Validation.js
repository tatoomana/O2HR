import React, { useEffect, useState, useCallback } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "@/components/ui/accordion";
import { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from "@/components/ui/tooltip";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { getValidation } from "@/lib/api";
import {
  CheckCircle2, XCircle, AlertTriangle, RefreshCw, Plug, Network, ShieldCheck,
  Database, ListChecks, Info,
} from "lucide-react";
import { toast } from "sonner";

const GROUP_ICONS = { plug: Plug, network: Network, shield: ShieldCheck, database: Database, check: ListChecks };

const StatusIcon = ({ status }) => {
  if (status === "pass") return <CheckCircle2 className="h-4 w-4 shrink-0" style={{ color: "var(--success)" }} />;
  if (status === "warn") return <AlertTriangle className="h-4 w-4 shrink-0" style={{ color: "var(--warning)" }} />;
  return <XCircle className="h-4 w-4 shrink-0" style={{ color: "var(--danger)" }} />;
};

export const Validation = () => {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    setError(false);
    getValidation()
      .then((d) => setReport(d))
      .catch(() => { setError(true); toast.error("Validation failed to load"); })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { load(); }, [load]);

  const summary = report?.summary || { passed: 0, failed: 0, warn: 0, total: 0 };
  const pct = summary.total ? Math.round((summary.passed / summary.total) * 100) : 0;
  const allPass = summary.total > 0 && summary.failed === 0;
  const ts = report?.generated_at ? new Date(report.generated_at).toLocaleTimeString() : "—";

  return (
    <Card className="border-border bg-card">
      {/* Header */}
      <div className="p-5 border-b border-border">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-semibold">Static validation report</h3>
              {allPass && (
                <Badge className="gap-1" style={{ background: "color-mix(in srgb, var(--success) 18%, transparent)", color: "var(--success)", border: "1px solid color-mix(in srgb, var(--success) 30%, transparent)" }}>
                  <CheckCircle2 className="h-3 w-3" /> All passing
                </Badge>
              )}
            </div>
            <p className="text-xs text-muted-foreground mt-1 font-mono">docker-free · parsed from docker-compose.yml · {ts}</p>
          </div>
          <Button data-testid="validation-refresh-button" variant="secondary" size="sm" onClick={load} className="border border-border rounded-lg">
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} /> Re-run
          </Button>
        </div>

        <div className="mt-4" data-testid="validation-status-summary">
          <div className="flex items-center justify-between text-xs mb-1.5">
            <span className="text-muted-foreground">{summary.passed}/{summary.total} checks passing</span>
            <span className="font-mono">{pct}%</span>
          </div>
          <Progress value={pct} className="h-2" />
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <Badge variant="secondary" className="gap-1"><CheckCircle2 className="h-3 w-3" style={{ color: "var(--success)" }} /> {summary.passed} pass</Badge>
            <Badge variant="secondary" className="gap-1"><XCircle className="h-3 w-3" style={{ color: "var(--danger)" }} /> {summary.failed} fail</Badge>
            <Badge variant="secondary" className="gap-1"><AlertTriangle className="h-3 w-3" style={{ color: "var(--warning)" }} /> {summary.warn} warn</Badge>
          </div>
        </div>
      </div>

      {/* Body */}
      <div className="p-5">
        {loading ? (
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-12 w-full rounded-lg" />)}
          </div>
        ) : error ? (
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription className="flex items-center justify-between gap-4">
              Could not run validation.
              <Button size="sm" variant="secondary" onClick={load}>Retry</Button>
            </AlertDescription>
          </Alert>
        ) : (
          <TooltipProvider delayDuration={150}>
            <Accordion type="multiple" defaultValue={(report?.groups || []).map((g) => g.name)} className="space-y-2">
              {(report?.groups || []).map((g) => {
                const Icon = GROUP_ICONS[g.icon] || ListChecks;
                const gp = g.checks.filter((c) => c.status === "pass").length;
                return (
                  <AccordionItem key={g.name} value={g.name} className="border border-border rounded-lg px-3 bg-background/40">
                    <AccordionTrigger className="hover:no-underline py-3">
                      <div className="flex items-center gap-2.5">
                        <Icon className="h-4 w-4 text-primary" />
                        <span className="text-sm font-medium">{g.name}</span>
                        <Badge variant="secondary" className="font-mono text-[10px]">{gp}/{g.checks.length}</Badge>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent>
                      <div className="flex flex-col gap-1 pb-2">
                        {g.checks.map((c) => (
                          <div key={c.name} className="flex items-center gap-2.5 rounded-md px-2 py-1.5 hover:bg-muted/60">
                            <StatusIcon status={c.status} />
                            <span className="text-sm">{c.name}</span>
                            {c.why && (
                              <Tooltip>
                                <TooltipTrigger asChild>
                                  <button className="ml-auto text-muted-foreground/70 hover:text-foreground" aria-label="why it matters">
                                    <Info className="h-3.5 w-3.5" />
                                  </button>
                                </TooltipTrigger>
                                <TooltipContent side="left" className="max-w-[260px] text-xs">{c.why}</TooltipContent>
                              </Tooltip>
                            )}
                          </div>
                        ))}
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                );
              })}
            </Accordion>
          </TooltipProvider>
        )}
      </div>
    </Card>
  );
};

export default Validation;
