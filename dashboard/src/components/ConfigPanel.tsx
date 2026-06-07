"use client";

import { useEffect, useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { useLang } from "@/context/LanguageContext";
import { toast } from "sonner";
import { Save, RotateCcw, Settings } from "lucide-react";

function flattenConfig(obj: Record<string, unknown>, prefix = ""): Record<string, string | boolean> {
  const result: Record<string, string | boolean> = {};
  for (const [k, v] of Object.entries(obj)) {
    const key = prefix ? `${prefix}.${k}` : k;
    if (v && typeof v === "object" && !Array.isArray(v)) {
      Object.assign(result, flattenConfig(v as Record<string, unknown>, key));
    } else if (typeof v === "boolean") {
      result[key] = v;
    } else {
      result[key] = String(v ?? "");
    }
  }
  return result;
}

function unflattenConfig(flat: Record<string, string | boolean>): Record<string, unknown> {
  const result: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(flat)) {
    const parts = key.split(".");
    let current = result;
    for (let i = 0; i < parts.length - 1; i++) {
      if (!(parts[i] in current)) current[parts[i]] = {};
      current = current[parts[i]] as Record<string, unknown>;
    }
    current[parts[parts.length - 1]] = value;
  }
  return result;
}

const SECTIONS = [
  { id: "adobe" as const, key: "config.sections.adobe" },
  { id: "openai" as const, key: "config.sections.openai" },
  { id: "providers" as const, key: "config.sections.providers" },
  { id: "output" as const, key: "config.sections.output" },
  { id: "metadata" as const, key: "config.sections.metadata" },
  { id: "browser" as const, key: "config.sections.browser" },
];

type SectionId = (typeof SECTIONS)[number]["id"];

export function ConfigPanel() {
  const { t } = useLang();
  const [values, setValues] = useState<Record<string, string | boolean>>({});
  const [loading, setLoading] = useState(true);
  const [activeSection, setActiveSection] = useState<SectionId>("adobe");

  const loadConfig = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/config");
      const data = await res.json();
      if (data.error) {
        toast.error(data.error);
        return;
      }
      setValues(flattenConfig(data));
    } catch {
      toast.error(t("config.loadError"));
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => {
    loadConfig();
  }, [loadConfig]);

  const updateValue = (key: string, value: string | boolean) => {
    setValues((prev) => ({ ...prev, [key]: value }));
  };

  const handleSave = async () => {
    const obj = unflattenConfig(values);
    try {
      const res = await fetch("/api/config", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(obj),
      });
      const data = await res.json();
      if (data.error) {
        toast.error(data.error);
      } else {
        toast.success(t("config.saved"));
        setValues(flattenConfig(data.config));
      }
    } catch {
      toast.error(t("config.saveError"));
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-lg font-semibold tracking-tight">{t("config.title")}</h2>
          <p className="text-sm text-muted-foreground mt-0.5">{t("common.loading")}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center ring-1 ring-primary/10">
          <Settings className="w-4.5 h-4.5 text-primary" />
        </div>
        <div className="flex-1">
          <h2 className="text-lg font-semibold tracking-tight">{t("config.title")}</h2>
          <p className="text-sm text-muted-foreground mt-0.5">{t("config.desc")}</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={loadConfig} className="border-border text-muted-foreground">
            <RotateCcw className="w-3.5 h-3.5 mr-1.5" />
            {t("config.reset")}
          </Button>
          <Button size="sm" onClick={handleSave} className="bg-foreground text-background hover:bg-foreground/90">
            <Save className="w-3.5 h-3.5 mr-1.5" />
            {t("config.save")}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-[180px_1fr] gap-5">
        {/* Section nav */}
        <div className="space-y-1">
          {SECTIONS.map((s) => (
            <button
              key={s.id}
              onClick={() => setActiveSection(s.id)}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-all ${
                activeSection === s.id
                  ? "bg-secondary text-foreground font-medium"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
              }`}
            >
              {t(s.key)}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="rounded-xl border border-border bg-[hsl(240_5%_9%)] p-5 min-h-[300px]">
          {activeSection === "adobe" && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">{t("config.adobe.email")}</Label>
                <Input value={String(values["adobe.contributor.email"] ?? "")} onChange={(e) => updateValue("adobe.contributor.email", e.target.value)} className="bg-[hsl(240_5%_8%)] border-border font-mono text-sm" />
              </div>
              <div className="space-y-2">
                <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">{t("config.adobe.password")}</Label>
                <Input type="password" value={String(values["adobe.contributor.password"] ?? "")} onChange={(e) => updateValue("adobe.contributor.password", e.target.value)} className="bg-[hsl(240_5%_8%)] border-border font-mono text-sm" />
              </div>
            </div>
          )}

          {activeSection === "openai" && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">{t("config.openai.apiKey")}</Label>
                <Input type="password" placeholder="sk-..." value={String(values["generation.openai.api_key"] ?? "")} onChange={(e) => updateValue("generation.openai.api_key", e.target.value)} className="bg-[hsl(240_5%_8%)] border-border font-mono text-sm" />
                <p className="text-xs text-muted-foreground/60 mt-1">{t("config.openai.apiKeyHint")}</p>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">{t("config.openai.model")}</Label>
                  <Input value={String(values["generation.openai.model"] ?? "dall-e-3")} onChange={(e) => updateValue("generation.openai.model", e.target.value)} className="bg-[hsl(240_5%_8%)] border-border text-sm" />
                </div>
                <div className="space-y-2">
                  <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">{t("config.openai.size")}</Label>
                  <Input value={String(values["generation.openai.size"] ?? "1792x1024")} onChange={(e) => updateValue("generation.openai.size", e.target.value)} className="bg-[hsl(240_5%_8%)] border-border text-sm" />
                </div>
              </div>
            </div>
          )}

          {activeSection === "providers" && (
            <div className="space-y-5">
              <div>
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3">{t("config.providers.defaultProvider")}</p>
                <Select value={String(values["generation.provider"] ?? "dummy")} onValueChange={(v) => v !== null && updateValue("generation.provider", v)}>
                  <SelectTrigger className="bg-[hsl(240_5%_8%)] border-border">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-[hsl(240_5%_10%)] border-border">
                    {["openai", "stability", "replicate", "local", "dummy", "chatgpt-web-gen", "baoyu-imagine"].map((p) => (
                      <SelectItem key={p} value={p}>{p}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-3">
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Stability</p>
                <Input type="password" placeholder="API Key" value={String(values["generation.stability.api_key"] ?? "")} onChange={(e) => updateValue("generation.stability.api_key", e.target.value)} className="bg-[hsl(240_5%_8%)] border-border font-mono text-sm" />
              </div>
              <div className="space-y-3">
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Replicate</p>
                <Input type="password" placeholder="API Token" value={String(values["generation.replicate.api_token"] ?? "")} onChange={(e) => updateValue("generation.replicate.api_token", e.target.value)} className="bg-[hsl(240_5%_8%)] border-border font-mono text-sm" />
              </div>
              <div className="space-y-3">
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Local (Diffusers)</p>
                <Input placeholder="Model ID" value={String(values["generation.local.model_id"] ?? "")} onChange={(e) => updateValue("generation.local.model_id", e.target.value)} className="bg-[hsl(240_5%_8%)] border-border text-sm" />
                <Input placeholder="Device (mps)" value={String(values["generation.local.device"] ?? "mps")} onChange={(e) => updateValue("generation.local.device", e.target.value)} className="bg-[hsl(240_5%_8%)] border-border text-sm" />
              </div>
            </div>
          )}

          {activeSection === "output" && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">{t("config.output.directory")}</Label>
                <Input value={String(values["output.dir"] ?? "./output")} onChange={(e) => updateValue("output.dir", e.target.value)} className="bg-[hsl(240_5%_8%)] border-border font-mono text-sm" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">{t("config.output.prefix")}</Label>
                  <Input value={String(values["output.prefix"] ?? "ads_")} onChange={(e) => updateValue("output.prefix", e.target.value)} className="bg-[hsl(240_5%_8%)] border-border font-mono text-sm" />
                </div>
                <div className="space-y-2">
                  <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">{t("config.output.jpegQuality")}</Label>
                  <Input value={String(values["output.quality"] ?? "95")} onChange={(e) => updateValue("output.quality", e.target.value)} className="bg-[hsl(240_5%_8%)] border-border font-mono text-sm" />
                </div>
              </div>
            </div>
          )}

          {activeSection === "metadata" && (
            <div className="space-y-5">
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">{t("config.metadata.language")}</Label>
                  <Input value={String(values["metadata.language"] ?? "en")} onChange={(e) => updateValue("metadata.language", e.target.value)} className="bg-[hsl(240_5%_8%)] border-border text-sm" />
                </div>
                <div className="space-y-2">
                  <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">{t("config.metadata.minKeywords")}</Label>
                  <Input value={String(values["metadata.min_keywords"] ?? "7")} onChange={(e) => updateValue("metadata.min_keywords", e.target.value)} className="bg-[hsl(240_5%_8%)] border-border text-sm" />
                </div>
              </div>
              <div className="flex items-center justify-between py-2">
                <div>
                  <p className="text-sm text-foreground/80">{t("config.metadata.aiGenerated")}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">{t("config.metadata.aiGeneratedHint")}</p>
                </div>
                <Switch checked={Boolean(values["metadata.ai_generated"])} onCheckedChange={(v) => updateValue("metadata.ai_generated", v)} />
              </div>
              <div className="flex items-center justify-between py-2">
                <div>
                  <p className="text-sm text-foreground/80">{t("config.metadata.hasReleases")}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">{t("config.metadata.hasReleasesHint")}</p>
                </div>
                <Switch checked={Boolean(values["metadata.has_releases"])} onCheckedChange={(v) => updateValue("metadata.has_releases", v)} />
              </div>
            </div>
          )}

          {activeSection === "browser" && (
            <div className="space-y-5">
              <div className="flex items-center justify-between py-2">
                <div>
                  <p className="text-sm text-foreground/80">{t("config.browser.headless")}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">{t("config.browser.headlessHint")}</p>
                </div>
                <Switch checked={Boolean(values["browser.headless"])} onCheckedChange={(v) => updateValue("browser.headless", v)} />
              </div>
              <div className="space-y-2">
                <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">{t("config.browser.slowMo")}</Label>
                <Input value={String(values["browser.slow_mo"] ?? "800")} onChange={(e) => updateValue("browser.slow_mo", e.target.value)} className="bg-[hsl(240_5%_8%)] border-border font-mono text-sm" />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
