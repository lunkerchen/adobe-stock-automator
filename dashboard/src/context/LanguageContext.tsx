"use client";

import { createContext, useContext, useState, useCallback, ReactNode } from "react";
import type { Lang } from "@/lib/i18n";
import { flattenTranslations, type FlatTranslations } from "@/lib/i18n";
import { translations } from "@/lib/translations";

interface LangContextValue {
  lang: Lang;
  setLang: (l: Lang) => void;
  t: (key: string, params?: Record<string, string | number>) => string;
}

const LangContext = createContext<LangContextValue | null>(null);

const cached: Record<string, FlatTranslations> = {};

function getFlat(lang: Lang): FlatTranslations {
  if (!cached[lang]) {
    cached[lang] = flattenTranslations(translations[lang] || translations["en"]);
  }
  return cached[lang];
}

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>("zh-TW");

  const setLang = useCallback((l: Lang) => {
    setLangState(l);
    if (typeof document !== "undefined") {
      document.documentElement.lang = l;
    }
  }, []);

  const t = useCallback(
    (key: string, params?: Record<string, string | number>): string => {
      const flat = getFlat(lang);
      let val = flat[key];
      if (!val) {
        // fallback to english
        const en = getFlat("en");
        val = en[key];
      }
      if (!val) return key;
      if (params) {
        for (const [k, v] of Object.entries(params)) {
          val = val.replace(`{${k}}`, String(v));
        }
      }
      return val;
    },
    [lang]
  );

  return (
    <LangContext.Provider value={{ lang, setLang, t }}>
      {children}
    </LangContext.Provider>
  );
}

export function useLang(): LangContextValue {
  const ctx = useContext(LangContext);
  if (!ctx) throw new Error("useLang must be used within LanguageProvider");
  return ctx;
}
