import { NextRequest } from "next/server";
import path from "path";
import { readdir, stat } from "fs/promises";
import { existsSync, readFileSync } from "fs";

const PROJECT_ROOT = path.resolve(process.cwd(), "..");
const OUTPUT_DIR = path.resolve(PROJECT_ROOT, "output");

// GET /api/images — list all generated images with metadata
export async function GET() {
  if (!existsSync(OUTPUT_DIR)) {
    return Response.json({ images: [] });
  }

  const files = await readdir(OUTPUT_DIR);
  const images = [];
  const csvPath = path.join(OUTPUT_DIR, "metadata.csv");

  // Parse metadata CSV
  const metadata: Record<string, Record<string, string>> = {};
  if (existsSync(csvPath)) {
    const csv = readFileSync(csvPath, "utf-8");
    const lines = csv.trim().split("\n");
    if (lines.length > 1) {
      const headers = lines[0].split(",").map((h) => h.trim());
      for (let i = 1; i < lines.length; i++) {
        const vals = lines[i].split(",").map((v) => v.trim().replace(/^"|"$/g, ""));
        const entry: Record<string, string> = {};
        headers.forEach((h, idx) => (entry[h] = vals[idx] || ""));
        metadata[entry["Filename"] || ""] = entry;
      }
    }
  }

  for (const file of files) {
    if (!/\.(jpg|jpeg|png|webp)$/i.test(file)) continue;
    const filepath = path.join(OUTPUT_DIR, file);
    const s = await stat(filepath);
    images.push({
      filename: file,
      path: `/api/output/${file}`,
      size: s.size,
      mtime: s.mtime.toISOString(),
      metadata: metadata[file] || null,
    });
  }

  // Sort by mtime, newest first
  images.sort((a, b) => new Date(b.mtime).getTime() - new Date(a.mtime).getTime());

  return Response.json({ images });
}
