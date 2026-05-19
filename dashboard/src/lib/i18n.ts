export type Lang = "zh-TW" | "en";

export interface TranslationMap {
  [key: string]: string | TranslationMap;
}

export type FlatTranslations = Record<string, string>;

export function flattenTranslations(obj: TranslationMap, prefix = ""): FlatTranslations {
  const result: FlatTranslations = {};
  for (const [key, value] of Object.entries(obj)) {
    const k = prefix ? `${prefix}.${key}` : key;
    if (typeof value === "string") {
      result[k] = value;
    } else {
      Object.assign(result, flattenTranslations(value as TranslationMap, k));
    }
  }
  return result;
}
