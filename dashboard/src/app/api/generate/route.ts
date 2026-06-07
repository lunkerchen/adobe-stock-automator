import { NextRequest } from "next/server";
import { spawn, SpawnOptionsWithoutStdio } from "child_process";
import path from "path";
import os from "os";
import { readdir, mkdir } from "fs/promises";
import { existsSync, readFileSync } from "fs";

const PROJECT_ROOT = path.resolve(process.cwd(), "..");
const OUTPUT_DIR = path.resolve(PROJECT_ROOT, "output");

type SSEData =
  | { type: "stdout"; text: string }
  | { type: "stderr"; text: string }
  | { type: "error"; message: string }
  | { type: "complete"; exitCode: number; images: { filename: string; path: string }[] };

function sseLine(data: SSEData): string {
  return `data: ${JSON.stringify(data)}\n\n`;
}

function readOpenAiApiKey(): string {
  // Priority: env var (used by Codex CLI) > config.yaml
  if (process.env.OPENAI_API_KEY) return process.env.OPENAI_API_KEY;
  try {
    const { load } = require("js-yaml");
    const text = readFileSync(path.join(PROJECT_ROOT, "config.yaml"), "utf-8");
    const cfg = load(text) as Record<string, any>;
    return cfg?.generation?.openai?.api_key || "";
  } catch {
    return "";
  }
}

// ── POST /api/generate ──
export async function POST(req: NextRequest) {
  const {
    prompt,
    count = 1,
    provider = "dummy",
    model,
    size,
    quality,
    format,
    submit = false,
  } = await req.json();

  if (!prompt) {
    return Response.json({ error: "prompt is required" }, { status: 400 });
  }

  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      const send = (data: SSEData) => {
        try { controller.enqueue(encoder.encode(sseLine(data))); }
        catch { /* controller closed */ }
      };

      if (provider === "gpt-image") {
        await runGptImage(send, prompt, count, model, size, quality, format);
      } else if (provider === "codex") {
        await runCodex(send, prompt, count);
      } else if (provider === "baoyu-imagine") {
        await runBaoyuImagine(send, prompt, count, model, size, quality, format);
      } else {
        await runMainPy(send, prompt, count, provider, submit);
      }
      controller.close();
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
}

// ── gpt-image provider ──
async function runGptImage(
  send: (d: SSEData) => void,
  prompt: string,
  count: number,
  model?: string,
  size?: string,
  quality?: string,
  format?: string,
) {
  const apiKey = readOpenAiApiKey();
  if (!apiKey) {
    send({ type: "error", message: "OPENAI_API_KEY not set. Add it in Config > OpenAI." });
    send({ type: "complete", exitCode: 1, images: [] });
    return;
  }

  if (!existsSync(OUTPUT_DIR)) {
    await mkdir(OUTPUT_DIR, { recursive: true });
  }

  const ext = format === "jpeg" ? "jpg" : format === "png" ? "png" : "webp";
  const generated: { filename: string; path: string }[] = [];

  for (let i = 0; i < count; i++) {
    const ts = Date.now();
    const filename = `gpt_${ts}_${i}.${ext}`;
    const filepath = path.join(OUTPUT_DIR, filename);

    send({ type: "stdout", text: `[${i + 1}/${count}] gpt-image generating...\n` });
    send({ type: "stdout", text: `  Model: ${model ?? "gpt-image-2"}  Size: ${size ?? "landscape"}  Quality: ${quality ?? "high"}\n` });

    await new Promise<void>((resolve) => {
      const opts: SpawnOptionsWithoutStdio = {
        cwd: PROJECT_ROOT,
        env: { ...process.env, OPENAI_API_KEY: apiKey } as NodeJS.ProcessEnv,
      };

      const args = ["-p", prompt, "-f", filepath];
      if (model) args.push("--model", model);
      if (size) args.push("--size", size);
      if (quality) args.push("--quality", quality);
      if (format) args.push("--format", format);

      const proc = spawn("gpt-image", args, opts);

      let errBuf = "";
      proc.stdout?.on("data", (chunk: Buffer) => send({ type: "stdout", text: chunk.toString() }));
      proc.stderr?.on("data", (chunk: Buffer) => {
        errBuf += chunk.toString();
        send({ type: "stderr", text: chunk.toString() });
      });
      proc.on("close", (code) => {
        if (code === 0) {
          generated.push({ filename, path: `/api/output/${filename}` });
          send({ type: "stdout", text: `  ✓ ${filename}\n` });
        } else {
          send({ type: "stderr", text: `  ✗ ${filename}: ${errBuf || `exit code ${code}`}\n` });
        }
        resolve();
      });
      proc.on("error", (err) => {
        send({ type: "stderr", text: `  ✗ ${filename}: ${err.message}\n` });
        resolve();
      });
    });
  }

  send({ type: "complete", exitCode: generated.length === count ? 0 : 1, images: generated });
}

// ── codex provider (ChatGPT subscription) ──
async function runCodex(
  send: (d: SSEData) => void,
  prompt: string,
  count: number,
) {
  if (!existsSync(OUTPUT_DIR)) {
    await mkdir(OUTPUT_DIR, { recursive: true });
  }

  const wrapper = path.resolve(PROJECT_ROOT, "dashboard", "scripts", "codex-gen-wrapper.sh");
  const generated: { filename: string; path: string }[] = [];

  for (let i = 0; i < count; i++) {
    const ts = Date.now();
    const filename = `codex_${ts}_${i}.png`;
    const filepath = path.join(OUTPUT_DIR, filename);

    send({ type: "stdout", text: `[${i + 1}/${count}] Codex generating via ChatGPT subscription...\n` });
    send({ type: "stdout", text: `  Prompt: ${prompt.slice(0, 80)}\n` });

    send({ type: "stdout", text: `  (This uses your ChatGPT subscription and takes ~30-60s)\n` });

    await new Promise<void>((resolve) => {
      const proc = spawn("bash", [wrapper, prompt, filepath, "180"], {
        cwd: PROJECT_ROOT,
        env: { ...process.env, HOME: os.homedir() } as NodeJS.ProcessEnv,
      });

      proc.stdout?.on("data", (chunk: Buffer) => {
        const text = chunk.toString();
        send({ type: "stdout", text });
      });
      proc.stderr?.on("data", (chunk: Buffer) => {
        send({ type: "stderr", text: chunk.toString() });
      });

      proc.on("close", (code) => {
        if (existsSync(filepath)) {
          generated.push({ filename, path: `/api/output/${filename}` });
          send({ type: "stdout", text: `  ✓ ${filename}\n` });
        } else {
          send({ type: "stderr", text: `  ✗ ${filename}: wrapper exited ${code}\n` });
        }
        resolve();
      });

      proc.on("error", (err) => {
        send({ type: "stderr", text: `  ✗ ${filename}: ${err.message}\n` });
        resolve();
      });
    });
  }

  send({ type: "complete", exitCode: generated.length === count ? 0 : 1, images: generated });
}

// ── baoyu-imagine provider ──
async function runBaoyuImagine(
  send: (d: SSEData) => void,
  prompt: string,
  count: number,
  model?: string,
  size?: string,
  quality?: string,
  format?: string,
) {
  const homeBin = path.join(os.homedir(), ".bun", "bin", "bun");
  const brewBin = "/opt/homebrew/bin/bun";
  const bun = existsSync(homeBin) ? homeBin : existsSync(brewBin) ? brewBin : "bun";

  const scriptPath = process.env.BAOYU_IMAGINE_SCRIPT
    || path.join(os.homedir(), ".agents", "skills", "baoyu-imagine", "scripts", "main.ts");

  if (!existsSync(scriptPath)) {
    send({ type: "error", message: `baoyu-imagine script not found: ${scriptPath}` });
    send({ type: "complete", exitCode: 1, images: [] });
    return;
  }

  if (!existsSync(OUTPUT_DIR)) {
    await mkdir(OUTPUT_DIR, { recursive: true });
  }

  const ext = format === "jpeg" ? "jpg" : "png";

  // Parse model value: "oai:gpt-image-2" -> { provider: "openai", model: "gpt-image-2" }
  const SUB_PROVIDER_MAP: Record<string, string> = {
    oai: "openai",
    goog: "google",
    ds: "dashscope",
    mm: "minimax",
    ark: "seedream",
  };
  let subProvider = "";
  let subModel = "";
  if (model && model.includes(":")) {
    const [prefix, ...rest] = model.split(":");
    subProvider = SUB_PROVIDER_MAP[prefix] || prefix;
    subModel = rest.join(":");
  } else if (model) {
    subModel = model;
  }

  const generated: { filename: string; path: string }[] = [];

  for (let i = 0; i < count; i++) {
    const ts = Date.now();
    const filename = `bai_${ts}_${i}.${ext}`;
    const filepath = path.join(OUTPUT_DIR, filename);

    send({ type: "stdout", text: `[${i + 1}/${count}] baoyu-imagine generating...\n` });
    send({ type: "stdout", text: `  Sub-provider: ${subProvider || "auto"}  Model: ${subModel || "auto"}  AR: ${size ?? "4:3"}  Quality: ${quality ?? "2k"}\n` });

    await new Promise<void>((resolve) => {
      const args = [scriptPath, "--prompt", prompt, "--image", filepath];
      if (subProvider) args.push("--provider", subProvider);
      if (subModel) args.push("--model", subModel);
      if (size) args.push("--ar", size);
      if (quality) args.push("--quality", quality);

      const opts: SpawnOptionsWithoutStdio = {
        cwd: PROJECT_ROOT,
        env: { ...process.env } as NodeJS.ProcessEnv,
      };

      const proc = spawn(bun, args, opts);

      let errBuf = "";
      proc.stdout?.on("data", (chunk: Buffer) => send({ type: "stdout", text: chunk.toString() }));
      proc.stderr?.on("data", (chunk: Buffer) => {
        errBuf += chunk.toString();
        send({ type: "stderr", text: chunk.toString() });
      });
      proc.on("close", (code) => {
        if (code === 0 && existsSync(filepath)) {
          generated.push({ filename, path: `/api/output/${filename}` });
          send({ type: "stdout", text: `  ✓ ${filename}\n` });
        } else {
          send({ type: "stderr", text: `  ✗ ${filename}: ${errBuf || `exit code ${code}`}\n` });
        }
        resolve();
      });
      proc.on("error", (err) => {
        send({ type: "stderr", text: `  ✗ ${filename}: ${err.message}\n` });
        resolve();
      });
    });
  }

  send({ type: "complete", exitCode: generated.length === count ? 0 : 1, images: generated });
}

// ── main.py fallback ──
async function runMainPy(
  send: (d: SSEData) => void,
  prompt: string,
  count: number,
  provider: string,
  submit: boolean,
): Promise<void> {
  return new Promise((resolve) => {
    const args = ["main.py", "generate", prompt, "-n", String(count)];
    if (provider) args.push("-p", provider);
    if (!submit) args.push("--no-submit");

    const opts: SpawnOptionsWithoutStdio = {
      cwd: PROJECT_ROOT,
      env: { ...process.env, PYTHONIOENCODING: "utf-8", FORCE_COLOR: "0" } as NodeJS.ProcessEnv,
    };

    const proc = spawn("python3", args, opts);

    proc.stdout?.on("data", (chunk: Buffer) => send({ type: "stdout", text: chunk.toString("utf-8") }));
    proc.stderr?.on("data", (chunk: Buffer) => send({ type: "stderr", text: chunk.toString("utf-8") }));

    proc.on("close", async (code) => {
      try {
        const files = await readdir(OUTPUT_DIR);
        const images = files
          .filter((f) => /\.(jpg|jpeg|png|webp)$/i.test(f))
          .map((f) => ({ filename: f, path: `/api/output/${f}` }));
        send({ type: "complete", exitCode: code ?? 0, images });
      } catch {
        send({ type: "complete", exitCode: code ?? 0, images: [] });
      }
      resolve();
    });

    proc.on("error", (err) => {
      send({ type: "error", message: err.message });
      resolve();
    });
  });
}
