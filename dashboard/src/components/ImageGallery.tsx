"use client";

import { useEffect, useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import { useLang } from "@/context/LanguageContext";
import { RotateCcw, ImageIcon, ExternalLink } from "lucide-react";

interface ImageMeta {
  filename: string;
  path: string;
  size: number;
  mtime: string;
  metadata: Record<string, string> | null;
}

interface Props {
  refreshKey: number;
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes}B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
}

function ImageCard({ img, onClick }: { img: ImageMeta; onClick: () => void }) {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);

  return (
    <button
      onClick={onClick}
      className="group relative rounded-xl overflow-hidden border border-border bg-[hsl(240_5%_9%)] text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 transition-all duration-200 hover:border-primary/20"
    >
      <div className="aspect-[4/3] bg-[hsl(240_5%_7%)] overflow-hidden relative">
        {!loaded && !error && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-5 h-5 border-2 border-border border-t-foreground/30 rounded-full animate-spin" />
          </div>
        )}
        {error ? (
          <div className="absolute inset-0 flex items-center justify-center text-muted-foreground">
            <ImageIcon className="w-6 h-6 opacity-30" />
          </div>
        ) : (
          <img
            src={img.path}
            alt={img.filename}
            className={`w-full h-full object-cover transition-all duration-500 ${
              loaded ? "opacity-100 scale-100" : "opacity-0 scale-95"
            } group-hover:scale-[1.03]`}
            onLoad={() => setLoaded(true)}
            onError={() => setError(true)}
            loading="lazy"
          />
        )}
      </div>
      <div className="p-2.5 space-y-1">
        <p className="text-xs font-mono truncate text-foreground/70">{img.filename}</p>
        <div className="flex items-center gap-2">
          <span className="text-[11px] text-muted-foreground">{formatBytes(img.size)}</span>
          <span className="text-[11px] text-muted-foreground">&middot;</span>
          <span className="text-[11px] text-muted-foreground">
            {(() => {
              const d = new Date(img.mtime);
              const diff = Date.now() - d.getTime();
              const mins = Math.floor(diff / 60000);
              if (mins < 1) return "just now";
              if (mins < 60) return `${mins}m ago`;
              return d.toLocaleDateString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
            })()}
          </span>
        </div>
      </div>
    </button>
  );
}

export function ImageGallery({ refreshKey }: Props) {
  const { t } = useLang();
  const [images, setImages] = useState<ImageMeta[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<ImageMeta | null>(null);

  const loadImages = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/images");
      const data = await res.json();
      setImages(data.images || []);
    } catch {
      // silent
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadImages();
  }, [loadImages, refreshKey]);

  // Keyboard nav
  useEffect(() => {
    if (!selected) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") setSelected(null);
      if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
        const idx = images.findIndex((i) => i.filename === selected.filename);
        if (idx === -1) return;
        const next = e.key === "ArrowRight"
          ? images[(idx + 1) % images.length]
          : images[(idx - 1 + images.length) % images.length];
        setSelected(next);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [selected, images]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center ring-1 ring-primary/10">
          <ImageIcon className="w-4.5 h-4.5 text-primary" />
        </div>
        <div className="flex-1">
          <h2 className="text-lg font-semibold tracking-tight">{t("gallery.title")}</h2>
          <p className="text-sm text-muted-foreground mt-0.5">
            {images.length > 0
              ? t("gallery.desc", { count: images.length })
              : t("gallery.descEmpty")}
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={loadImages}
          disabled={loading}
          className="border-border text-muted-foreground hover:text-foreground"
        >
          <RotateCcw className={`w-3.5 h-3.5 mr-1.5 ${loading ? "animate-spin" : ""}`} />
          {t("gallery.refresh")}
        </Button>
      </div>

      {/* Grid */}
      {loading && images.length === 0 ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="rounded-xl overflow-hidden border border-border bg-[hsl(240_5%_9%)] animate-pulse">
              <div className="aspect-[4/3] bg-[hsl(240_5%_7%)]" />
              <div className="p-2.5 space-y-2">
                <div className="h-3 bg-[hsl(240_5%_12%)] rounded w-3/4" />
                <div className="h-2 bg-[hsl(240_5%_12%)] rounded w-1/2" />
              </div>
            </div>
          ))}
        </div>
      ) : images.length === 0 ? (
        <div className="rounded-xl border border-border bg-[hsl(240_5%_9%)] flex flex-col items-center justify-center py-20 text-muted-foreground">
          <ImageIcon className="w-12 h-12 mb-4 opacity-15" />
          <p className="text-sm">{t("gallery.noImages")}</p>
          <p className="text-xs mt-1.5 opacity-60">{t("gallery.noImagesHint")}</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
          {images.map((img) => (
            <ImageCard key={img.filename} img={img} onClick={() => setSelected(img)} />
          ))}
        </div>
      )}

      {/* Lightbox */}
      <Dialog open={!!selected} onOpenChange={(o) => !o && setSelected(null)}>
        <DialogContent className="max-w-5xl bg-[hsl(240_5%_8%)] border-border p-0 overflow-hidden rounded-2xl">
          <DialogTitle className="sr-only">{t("common.close")}</DialogTitle>
          {selected && (
            <div>
              <div className="bg-[hsl(240_5%_5%)] flex items-center justify-center p-4">
                <img
                  src={selected.path}
                  alt={selected.filename}
                  className="max-h-[65vh] object-contain rounded-lg"
                />
              </div>
              <div className="px-5 py-3 border-t border-border flex items-center justify-between">
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-mono text-foreground/80 truncate">{selected.filename}</p>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="text-xs text-muted-foreground">{formatBytes(selected.size)}</span>
                    <span className="text-xs text-muted-foreground">&middot;</span>
                    <span className="text-xs text-muted-foreground">{new Date(selected.mtime).toLocaleString()}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  {selected.metadata && (
                    <Badge variant="outline" className="text-[10px] border-border text-muted-foreground">
                      {t("gallery.aiGenerated")}
                    </Badge>
                  )}
                  <a href={selected.path} target="_blank" rel="noopener noreferrer">
                    <Button variant="outline" size="sm" className="border-border">
                      <ExternalLink className="w-3.5 h-3.5" />
                    </Button>
                  </a>
                </div>
              </div>
              {selected.metadata && (
                <div className="px-5 pb-4">
                  <div className="rounded-lg bg-[hsl(240_5%_10%)] border border-border overflow-hidden">
                    <div className="px-3 py-2 border-b border-border">
                      <span className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">
                        {t("gallery.metadata")}
                      </span>
                    </div>
                    <div className="p-3 grid grid-cols-2 gap-x-4 gap-y-1.5 text-xs">
                      {Object.entries(selected.metadata).map(([k, v]) => (
                        <div key={k} className="flex gap-2 min-w-0">
                          <span className="text-muted-foreground shrink-0 w-20">{k}</span>
                          <span className="text-foreground/70 truncate">{v || "—"}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
