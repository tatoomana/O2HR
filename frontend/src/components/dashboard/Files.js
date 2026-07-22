import React, { useEffect, useMemo, useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Input } from "@/components/ui/input";
import { CodeBlock } from "./CodeBlock";
import { listFiles, getFile, fileDownloadUrl } from "@/lib/api";
import { FileCode, FileText, Settings, GitBranch, Terminal, Download, Search } from "lucide-react";
import { toast } from "sonner";

const slug = (name) =>
  name.replace(/[^a-zA-Z0-9]+/g, "-").replace(/^-|-$/g, "").toLowerCase();

const iconFor = (name) => {
  if (name.endsWith(".sh")) return Terminal;
  if (name.endsWith(".md")) return FileText;
  if (name.endsWith(".py")) return FileCode;
  if (name.endsWith(".yml") || name.endsWith(".yaml")) return FileCode;
  if (name.includes("env")) return Settings;
  if (name.includes("gitignore")) return GitBranch;
  return FileCode;
};

const fmtSize = (n) => (n < 1024 ? `${n} B` : `${(n / 1024).toFixed(1)} KB`);

export const Files = () => {
  const [files, setFiles] = useState([]);
  const [selected, setSelected] = useState(null);
  const [content, setContent] = useState(null);
  const [loadingList, setLoadingList] = useState(true);
  const [loadingContent, setLoadingContent] = useState(false);
  const [query, setQuery] = useState("");

  useEffect(() => {
    let active = true;
    listFiles()
      .then((fs) => {
        if (!active) return;
        setFiles(fs);
        const first = fs.find((f) => f.primary) || fs[0];
        if (first) setSelected(first.name);
      })
      .catch(() => toast.error("Failed to load file list"))
      .finally(() => active && setLoadingList(false));
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (!selected) return;
    let active = true;
    setLoadingContent(true);
    getFile(selected)
      .then((data) => active && setContent(data))
      .catch(() => toast.error(`Failed to load ${selected}`))
      .finally(() => active && setLoadingContent(false));
    return () => { active = false; };
  }, [selected]);

  const filtered = useMemo(
    () => files.filter((f) => f.name.toLowerCase().includes(query.toLowerCase())),
    [files, query]
  );

  return (
    <div className="grid lg:grid-cols-12 gap-5">
      {/* File list */}
      <div className="lg:col-span-4">
        <Card className="border-border bg-card p-3">
          <div className="relative mb-3">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              data-testid="files-search-input"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Filter files…"
              className="pl-8 h-9 bg-background"
            />
          </div>
          <div className="flex flex-col gap-1">
            {loadingList
              ? Array.from({ length: 6 }).map((_, i) => (
                  <Skeleton key={i} className="h-14 w-full rounded-lg" />
                ))
              : filtered.map((f) => {
                  const Icon = iconFor(f.name);
                  const isActive = selected === f.name;
                  return (
                    <button
                      key={f.name}
                      data-testid={`files-filelist-item-${slug(f.name)}`}
                      onClick={() => setSelected(f.name)}
                      className={`w-full text-left rounded-lg border px-3 py-2.5 transition-colors ${
                        isActive
                          ? "border-primary/40 bg-primary/10"
                          : "border-transparent hover:bg-muted"
                      }`}
                    >
                      <div className="flex items-center gap-2.5">
                        <Icon className={`h-4 w-4 shrink-0 ${isActive ? "text-primary" : "text-muted-foreground"}`} />
                        <span className="font-mono text-sm truncate">{f.name}</span>
                      </div>
                      <div className="mt-1 flex items-center gap-2 pl-7">
                        <Badge variant="secondary" className="text-[10px] uppercase">{f.language}</Badge>
                        <span className="text-[11px] text-muted-foreground font-mono">{f.lines} lines · {fmtSize(f.size)}</span>
                      </div>
                    </button>
                  );
                })}
            {!loadingList && filtered.length === 0 && (
              <div className="text-sm text-muted-foreground py-6 text-center">No files match “{query}”</div>
            )}
          </div>
        </Card>
      </div>

      {/* Code panel */}
      <div className="lg:col-span-8">
        <Card className="border-border bg-card overflow-hidden">
          <div className="flex items-center justify-between gap-3 border-b border-border px-4 py-3">
            <div className="min-w-0">
              <div className="font-mono text-sm truncate">{selected || "—"}</div>
              {content && (
                <div className="text-[11px] text-muted-foreground mt-0.5">{content.description}</div>
              )}
            </div>
            <div className="flex items-center gap-2 shrink-0">
              {content && <Badge variant="secondary" className="text-[10px] uppercase">{content.language}</Badge>}
              {content && <span className="hidden sm:inline text-[11px] text-muted-foreground font-mono">{content.lines} L</span>}
              {selected && (
                <a
                  data-testid="codepanel-download-button"
                  href={fileDownloadUrl(selected)}
                  className="inline-flex h-8 items-center gap-1.5 rounded-lg border border-border bg-background px-2.5 text-xs hover:bg-muted transition-colors"
                  onClick={() => toast.success(`Downloading ${selected}`)}
                >
                  <Download className="h-3.5 w-3.5" /> Download
                </a>
              )}
            </div>
          </div>
          <div className="p-3">
            {loadingContent || !content ? (
              <div className="space-y-2 p-2">
                {Array.from({ length: 12 }).map((_, i) => (
                  <Skeleton key={i} className="h-4" style={{ width: `${60 + ((i * 7) % 38)}%` }} />
                ))}
              </div>
            ) : (
              <CodeBlock
                code={content.content}
                language={content.language}
                maxHeight="560px"
                testId="codepanel-copy-button"
              />
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Files;
