"use client";

import { useState } from "react";
import { GeneratePanel } from "@/components/GeneratePanel";
import { ImageGallery } from "@/components/ImageGallery";
import { ConfigPanel } from "@/components/ConfigPanel";
import { useLang } from "@/context/LanguageContext";
import { Image, Sparkles, Settings, Globe } from "lucide-react";
import type { Lang } from "@/lib/i18n";

const TABS = [
  { id: "generate", icon: Sparkles, key: "nav.generate" },
  { id: "gallery", icon: Image, key: "nav.gallery" },
  { id: "config", icon: Settings, key: "nav.config" },
] as const;

type TabId = (typeof TABS)[number]["id"];

const LANGS: { label: string; value: Lang }[] = [
  { label: "繁體中文", value: "zh-TW" },
  { label: "English", value: "en" },
];

export default function Home() {
  const [activeTab, setActiveTab] = useState<TabId>("generate");
  const [refreshKey, setRefreshKey] = useState(0);
  const { lang, setLang, t } = useLang();

  const onGenerationDone = () => setRefreshKey((k) => k + 1);

  return (
    <div className="min-h-screen flex bg-[hsl(240_6%_7%)]">
      {/* Sidebar */}
      <aside className="w-60 shrink-0 border-r border-border bg-[hsl(240_5%_8%)] flex flex-col select-none">
        {/* Brand */}
        <div className="px-5 pt-6 pb-5 border-b border-border">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-primary/25 to-primary/10 flex items-center justify-center ring-1 ring-primary/10">
              <Image className="w-4 h-4 text-primary" />
            </div>
            <div>
              <h1 className="text-sm font-semibold tracking-tight">{t("app.name")}</h1>
              <p className="text-[11px] text-muted-foreground mt-0.5">{t("app.subtitle")}</p>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {TABS.map((tab) => {
            const Icon = tab.icon;
            const active = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-150 ${
                  active
                    ? "bg-secondary text-foreground font-medium shadow-sm"
                    : "text-muted-foreground hover:text-foreground hover:bg-secondary/40"
                }`}
              >
                <Icon className="w-4 h-4 shrink-0" />
                {t(tab.key)}
              </button>
            );
          })}
        </nav>

        {/* Lang + version */}
        <div className="px-3 py-3 border-t border-border space-y-2">
          {/* Language selector */}
          <div className="flex items-center gap-1.5 px-2 py-1.5 rounded-lg bg-[hsl(240_5%_6%)] border border-border/50">
            <Globe className="w-3.5 h-3.5 text-muted-foreground shrink-0" />
            {LANGS.map((l) => (
              <button
                key={l.value}
                onClick={() => setLang(l.value)}
                className={`text-[11px] px-2 py-0.5 rounded-md transition-all ${
                  lang === l.value
                    ? "bg-foreground/10 text-foreground font-medium"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {l.label}
              </button>
            ))}
          </div>
          <p className="text-[10px] text-muted-foreground/60 text-center">
            {t("app.version")} &middot; {t("app.tagline")}
          </p>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-auto">
        <div className="max-w-6xl mx-auto p-6 lg:p-8 animate-in fade-in duration-300">
          {activeTab === "generate" && <GeneratePanel onDone={onGenerationDone} />}
          {activeTab === "gallery" && <ImageGallery refreshKey={refreshKey} />}
          {activeTab === "config" && <ConfigPanel />}
        </div>
      </main>
    </div>
  );
}
