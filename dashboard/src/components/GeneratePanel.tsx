"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { useLang } from "@/context/LanguageContext";
import { PROVIDER_CONFIGS } from "@/lib/modelConfig";
import { toast } from "sonner";
import {
  Loader2,
  Play,
  Square,
  Terminal,
  CheckCircle2,
  Image as ImageIcon,
  Sparkles,
} from "lucide-react";

const PROVIDERS = Object.keys(PROVIDER_CONFIGS);

interface Props {
  onDone: () => void;
}

interface LogEntry {
  type: "stdout" | "stderr" | "info" | "error";
  text: string;
}

export function GeneratePanel({ onDone }: Props) {
  const { t } = useLang();
  const [prompt, setPrompt] = useState("");
  const [count, setCount] = useState("1");
  const [provider, setProvider] = useState("codex");
  const [running, setRunning] = useState(false);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [checkImages, setCheckImages] = useState<{ filename: string; path: string }[]>([]);
  const abortRef = useRef<AbortController | null>(null);
  const logEndRef = useRef<HTMLDivElement>(null);

  // Model config for current provider
  const cfg = PROVIDER_CONFIGS[provider];
  const [model, setModel] = useState(cfg?.defaultModel ?? "");
  const [size, setSize] = useState(cfg?.defaultSize ?? "");
  const [quality, setQuality] = useState(cfg?.defaultQuality ?? "");
  const [format, setFormat] = useState(cfg?.defaultFormat ?? "");

  // Reset model options when provider changes
  useEffect(() => {
    const c = PROVIDER_CONFIGS[provider];
    if (c) {
      setModel(c.defaultModel);
      setSize(c.defaultSize);
      setQuality(c.defaultQuality);
      setFormat(c.defaultFormat);
    }
  }, [provider]);

  // Auto-scroll logs
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const handleGenerate = useCallback(async () => {
    if (!prompt.trim()) {
      toast.error(t("generate.enterPrompt"));
      return;
    }

    setRunning(true);
    setLogs([{ type: "info", text: t("generate.startLog") }]);
    setCheckImages([]);

    const ctrl = new AbortController();
    abortRef.current = ctrl;

    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: prompt.trim(),
          count: parseInt(count) || 1,
          provider,
          model,
          size,
          quality,
          format,
          submit: false,
        }),
        signal: ctrl.signal,
      });

      const reader = res.body?.getReader();
      if (!reader) throw new Error("No response body");

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          try {
            const data = JSON.parse(line.slice(6));
            switch (data.type) {
              case "stdout":
                setLogs((prev) => [...prev, { type: "stdout", text: data.text }]);
                break;
              case "stderr":
                setLogs((prev) => [...prev, { type: "stderr", text: data.text }]);
                break;
              case "error":
                setLogs((prev) => [...prev, { type: "error", text: data.message }]);
                toast.error(data.message);
                break;
              case "complete":
                setLogs((prev) => [
                  ...prev,
                  {
                    type: "info",
                    text:
                      data.exitCode === 0
                        ? t("generate.done", { count: data.images.length })
                        : t("generate.failed", { code: data.exitCode }),
                  },
                ]);
                if (data.images?.length) {
                  setCheckImages(data.images);
                }
                toast.success(
                  data.exitCode === 0
                    ? t("generate.generated", { count: data.images.length })
                    : t("generate.generationFailed")
                );
                onDone();
                break;
            }
          } catch {
            // skip unparseable lines
          }
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error && err.name === "AbortError") {
        setLogs((prev) => [...prev, { type: "info", text: t("generate.cancelled") }]);
      } else {
        const msg = err instanceof Error ? err.message : String(err);
        setLogs((prev) => [...prev, { type: "error", text: msg }]);
        toast.error(msg);
      }
    } finally {
      setRunning(false);
      abortRef.current = null;
    }
  }, [prompt, count, provider, model, size, quality, format, t, onDone]);

  const handleCancel = () => abortRef.current?.abort();
  const handleClear = () => {
    setLogs([]);
    setCheckImages([]);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center ring-1 ring-primary/10">
          <Sparkles className="w-4.5 h-4.5 text-primary" />
        </div>
        <div>
          <h2 className="text-lg font-semibold tracking-tight">{t("generate.title")}</h2>
          <p className="text-sm text-muted-foreground mt-0.5">{t("generate.desc")}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Control Panel — 2 cols */}
        <div className="lg:col-span-2 space-y-5">
          {/* Prompt */}
          <div className="space-y-2">
            <Label htmlFor="prompt" className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
              {t("generate.prompt")}
            </Label>
            <Textarea
              id="prompt"
              placeholder={t("generate.promptPlaceholder")}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="min-h-[130px] resize-none bg-[hsl(240_5%_9%)] border-border focus:border-primary/30 transition-colors"
              disabled={running}
            />
          </div>

          {/* Provider + Model */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-2">
              <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                {t("generate.provider")}
              </Label>
              <Select value={provider} onValueChange={(v) => v !== null && setProvider(v)} disabled={running}>
                <SelectTrigger className="bg-[hsl(240_5%_9%)] border-border">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-[hsl(240_5%_10%)] border-border z-50">
                  {PROVIDERS.map((p) => (
                    <SelectItem key={p} value={p}>{p}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                {t("generate.model")}
              </Label>
              <Select value={model} onValueChange={(v) => v !== null && setModel(v)} disabled={running}>
                <SelectTrigger className="bg-[hsl(240_5%_9%)] border-border">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-[hsl(240_5%_10%)] border-border z-50">
                  {cfg?.models.map((m) => (
                    <SelectItem key={m.value} value={m.value}>{m.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Count + Size */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-2">
              <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                {t("generate.count")}
              </Label>
              <Input
                type="number" min={1} max={10}
                value={count}
                onChange={(e) => setCount(e.target.value)}
                className="bg-[hsl(240_5%_9%)] border-border"
                disabled={running}
              />
            </div>
            <div className="space-y-2">
              <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                {t("generate.size")}
              </Label>
              <Select value={size} onValueChange={(v) => v !== null && setSize(v)} disabled={running}>
                <SelectTrigger className="bg-[hsl(240_5%_9%)] border-border">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-[hsl(240_5%_10%)] border-border z-50">
                  {cfg?.sizes.map((s) => (
                    <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Quality + Format */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-2">
              <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                {t("generate.quality")}
              </Label>
              <Select value={quality} onValueChange={(v) => v !== null && setQuality(v)} disabled={running}>
                <SelectTrigger className="bg-[hsl(240_5%_9%)] border-border">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-[hsl(240_5%_10%)] border-border z-50">
                  {cfg?.qualities.map((q) => (
                    <SelectItem key={q.value} value={q.value}>{q.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                {t("generate.format")}
              </Label>
              <Select value={format} onValueChange={(v) => v !== null && setFormat(v)} disabled={running}>
                <SelectTrigger className="bg-[hsl(240_5%_9%)] border-border">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-[hsl(240_5%_10%)] border-border z-50">
                  {cfg?.formats.map((f) => (
                    <SelectItem key={f.value} value={f.value}>{f.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-2 pt-1">
            {running ? (
              <Button variant="destructive" onClick={handleCancel} className="flex-1">
                <Square className="w-4 h-4 mr-2 fill-current" />
                {t("generate.cancel")}
              </Button>
            ) : (
              <Button
                onClick={handleGenerate}
                disabled={!prompt.trim()}
                className="flex-1 bg-foreground text-background hover:bg-foreground/90"
              >
                <Play className="w-4 h-4 mr-2 fill-current" />
                {t("generate.generate")}
              </Button>
            )}
            <Button variant="outline" onClick={handleClear} disabled={running} className="border-border">
              {t("generate.clear")}
            </Button>
          </div>
        </div>

        {/* Output Panel — 3 cols */}
        <div className="lg:col-span-3 space-y-4">
          {/* Terminal */}
          <div className="rounded-xl overflow-hidden border border-border bg-[hsl(240_5%_8%)]">
            <div className="flex items-center justify-between px-4 py-2.5 bg-[hsl(240_5%_10%)] border-b border-border">
              <div className="flex items-center gap-2">
                <div className="flex gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-red-500/60" />
                  <span className="w-2.5 h-2.5 rounded-full bg-yellow-500/60" />
                  <span className="w-2.5 h-2.5 rounded-full bg-green-500/60" />
                </div>
                <span className="text-xs text-muted-foreground ml-2 font-mono">{t("generate.output")}</span>
              </div>
              {running && (
                <Badge variant="outline" className="text-amber-400/80 border-amber-600/30 text-[10px] h-5">
                  <Loader2 className="w-2.5 h-2.5 mr-1 animate-spin" />
                  {t("generate.running")}
                </Badge>
              )}
            </div>
            <div className="terminal-log h-[340px] overflow-y-auto p-4 font-mono text-xs leading-relaxed space-y-0.5">
              {logs.length === 0 && (
                <p className="text-muted-foreground/40 italic select-none">
                  {t("generate.noOutput")}
                </p>
              )}
              {logs.map((entry, i) => (
                <div
                  key={i}
                  className={`${
                    entry.type === "stderr"
                      ? "text-red-400/80"
                      : entry.type === "error"
                        ? "text-red-400 font-semibold"
                        : entry.type === "info"
                          ? "text-muted-foreground"
                          : "text-foreground/80"
                  }`}
                >
                  {entry.type === "stdout" && (
                    <Terminal className="w-3 h-3 inline mr-1.5 opacity-30 shrink-0" />
                  )}
                  {entry.text}
                </div>
              ))}
              {running && (
                <div className="flex items-center gap-2 text-muted-foreground pt-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                  {t("generate.processing")}
                </div>
              )}
              <div ref={logEndRef} />
            </div>
          </div>

          {/* Generated images */}
          {checkImages.length > 0 && (
            <div className="rounded-xl border border-border bg-[hsl(240_5%_9%)] p-4">
              <div className="flex items-center gap-2 mb-3">
                <CheckCircle2 className="w-4 h-4 text-green-500/70" />
                <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  {t("generate.generatedImages")}
                </span>
                <Badge variant="outline" className="ml-auto text-[10px] border-border text-muted-foreground">
                  {checkImages.length}
                </Badge>
              </div>
              <div className="flex gap-3 flex-wrap">
                {checkImages.map((img) => (
                  <a
                    key={img.filename}
                    href={img.path}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="group block w-28 h-20 rounded-lg overflow-hidden border border-border bg-[hsl(240_5%_7%)] hover:border-primary/30 transition-all duration-200"
                  >
                    <img
                      src={img.path}
                      alt={img.filename}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
