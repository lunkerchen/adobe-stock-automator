import { NextRequest } from "next/server";
import path from "path";
import { readFile } from "fs/promises";
import { existsSync } from "fs";

const PROJECT_ROOT = path.resolve(process.cwd(), "..");
const OUTPUT_DIR = path.resolve(PROJECT_ROOT, "output");

// GET /api/output/:filename — serve generated images
export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ filename: string }> }
) {
  const { filename } = await params;

  // Security: prevent path traversal
  if (filename.includes("..") || filename.includes("/")) {
    return new Response("Forbidden", { status: 403 });
  }

  const filepath = path.join(OUTPUT_DIR, filename);
  if (!existsSync(filepath)) {
    return new Response("Not found", { status: 404 });
  }

  const buf = await readFile(filepath);
  const ext = path.extname(filename).toLowerCase();
  const mime: Record<string, string> = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
  };

  return new Response(buf, {
    headers: {
      "Content-Type": mime[ext] || "application/octet-stream",
      "Cache-Control": "public, max-age=3600",
    },
  });
}
