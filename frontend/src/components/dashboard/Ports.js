import React from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { CheckCircle2, Ban } from "lucide-react";

const rows = [
  { service: "OpenHands", host: "5000", container: "3000", note: "Web UI (mapped away from forbidden :3000)", ok: true },
  { service: "Headroom", host: "5001", container: "8787", note: "Proxy / UI bound to 0.0.0.0", ok: true },
];

export const Ports = () => {
  return (
    <Card className="border-border bg-card overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow className="hover:bg-transparent">
            <TableHead>Service</TableHead>
            <TableHead className="font-mono">Host Port</TableHead>
            <TableHead className="font-mono">Container Port</TableHead>
            <TableHead>Notes</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((r) => (
            <TableRow key={r.service} data-testid={`ports-row-${r.service.toLowerCase()}`}>
              <TableCell className="font-medium">
                <span className="inline-flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4" style={{ color: "var(--success)" }} />
                  {r.service}
                </span>
              </TableCell>
              <TableCell>
                <Badge variant="secondary" className="font-mono">{r.host}</Badge>
              </TableCell>
              <TableCell className="font-mono text-muted-foreground">{r.container}</TableCell>
              <TableCell className="text-muted-foreground">{r.note}</TableCell>
            </TableRow>
          ))}
          <TableRow data-testid="ports-forbidden-ports-row" className="bg-destructive/5 hover:bg-destructive/10">
            <TableCell className="font-medium">
              <span className="inline-flex items-center gap-2">
                <Ban className="h-4 w-4" style={{ color: "var(--danger)" }} />
                Forbidden
              </span>
            </TableCell>
            <TableCell>
              <Badge variant="destructive" className="font-mono">3000</Badge>{" "}
              <Badge variant="destructive" className="font-mono">4000</Badge>
            </TableCell>
            <TableCell className="font-mono text-muted-foreground">—</TableCell>
            <TableCell className="text-muted-foreground">Never bound on the host (reserved / in use)</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </Card>
  );
};

export default Ports;
