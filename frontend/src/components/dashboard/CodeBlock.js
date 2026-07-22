import React, { useState } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { Copy, Check } from "lucide-react";
import { toast } from "sonner";

export const CodeBlock = ({
  code = "",
  language = "bash",
  showLineNumbers = true,
  maxHeight = "260px",
  testId,
}) => {
  const [copied, setCopied] = useState(false);

  const onCopy = () => {
    navigator.clipboard
      .writeText(code)
      .then(() => {
        setCopied(true);
        toast.success("Copied to clipboard");
        setTimeout(() => setCopied(false), 1200);
      })
      .catch(() => toast.error("Copy failed"));
  };

  return (
    <div className="relative group rounded-xl border overflow-hidden"
      style={{ borderColor: "var(--code-border)", background: "var(--code-bg)" }}>
      <button
        type="button"
        aria-label="Copy code"
        data-testid={testId}
        onClick={onCopy}
        className="absolute right-2 top-2 z-10 inline-flex h-8 w-8 items-center justify-center rounded-lg border border-border bg-card/70 text-foreground/80 backdrop-blur transition-colors hover:bg-muted hover:text-foreground"
      >
        {copied ? (
          <Check className="h-4 w-4" style={{ color: "var(--success)" }} />
        ) : (
          <Copy className="h-4 w-4" />
        )}
      </button>
      <div className="thin-scroll" style={{ maxHeight, overflow: "auto" }}>
        <SyntaxHighlighter
          language={language}
          style={oneDark}
          showLineNumbers={showLineNumbers}
          wrapLongLines={false}
          customStyle={{
            margin: 0,
            background: "transparent",
            fontSize: "12.5px",
            padding: "16px",
          }}
          lineNumberStyle={{ color: "#3b465a", minWidth: "2.4em" }}
          codeTagProps={{
            style: { fontFamily: "'JetBrains Mono', ui-monospace, monospace" },
          }}
        >
          {code}
        </SyntaxHighlighter>
      </div>
    </div>
  );
};

export default CodeBlock;
