import React from "react";
import { Card } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { CodeBlock } from "./CodeBlock";
import { Lightbulb } from "lucide-react";

const steps = [
  {
    n: 1,
    title: "Prepare the host",
    desc: "Creates ./workspace, detects the docker socket GID, and writes host-specific values into .env.",
    code: "./init.sh",
    lang: "bash",
  },
  {
    n: 2,
    title: "Add your GLM / Z.AI key",
    desc: "The only value you must edit by hand. Everything else is auto-filled.",
    code: "# in .env\nLLM_API_KEY=your_zai_glm_api_key_here",
    lang: "bash",
  },
  {
    n: 3,
    title: "Launch the stack",
    desc: "Pulls images and starts both services detached. UIs come up on :5000 and :5001.",
    code: "docker compose up -d",
    lang: "bash",
  },
];

export const QuickStart = () => {
  return (
    <div className="space-y-5">
      <div className="grid md:grid-cols-3 gap-5">
        {steps.map((s) => (
          <Card key={s.n} className="border-border bg-card p-5 flex flex-col">
            <div className="flex items-center gap-3 mb-3">
              <div className="h-8 w-8 rounded-lg grid place-items-center bg-primary text-primary-foreground font-semibold text-sm">
                {s.n}
              </div>
              <div className="font-medium">{s.title}</div>
            </div>
            <p className="text-sm text-muted-foreground mb-4 leading-relaxed flex-1">{s.desc}</p>
            <CodeBlock code={s.code} language={s.lang} showLineNumbers={false} maxHeight="90px" testId={`quickstart-copy-step-${s.n}`} />
          </Card>
        ))}
      </div>

      <Alert className="border-border bg-card">
        <Lightbulb className="h-4 w-4 text-primary" />
        <AlertTitle>Socket permission mismatch?</AlertTitle>
        <AlertDescription className="text-muted-foreground">
          If OpenHands reports <span className="font-mono">permission denied</span> on the docker socket, just
          re-run <span className="font-mono">./init.sh</span> — it recomputes <span className="font-mono">DOCKER_GID</span>{" "}
          from the live socket. Never <span className="font-mono">chmod 666</span> the socket.
        </AlertDescription>
      </Alert>
    </div>
  );
};

export default QuickStart;
