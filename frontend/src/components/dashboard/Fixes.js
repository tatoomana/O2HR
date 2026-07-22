import React from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { CodeBlock } from "./CodeBlock";
import { ShieldCheck, Network } from "lucide-react";

const ICONS = { shield: ShieldCheck, network: Network };

export const Fixes = ({ fixes = [] }) => {
  return (
    <div className="grid md:grid-cols-2 gap-5">
      {fixes.map((f) => {
        const Icon = ICONS[f.icon] || ShieldCheck;
        return (
          <Card key={f.id} data-testid={`fix-card-${f.id}`} className="border-border bg-card flex flex-col">
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-xl grid place-items-center bg-primary/12 border border-primary/25">
                  <Icon className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <CardTitle className="text-lg">{f.title}</CardTitle>
                  <CardDescription className="text-xs mt-0.5">The #1 reason this stack used to fail</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col gap-4">
              <p className="text-sm text-muted-foreground leading-relaxed">{f.summary}</p>
              <div className="mt-auto">
                <CodeBlock code={f.snippet} language="yaml" showLineNumbers={false} maxHeight="200px" testId={`fix-copy-${f.id}`} />
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
};

export default Fixes;
