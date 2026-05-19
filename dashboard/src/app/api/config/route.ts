import { NextRequest } from "next/server";
import { spawnSync } from "child_process";
import path from "path";

const PROJECT_ROOT = path.resolve(process.cwd(), "..");
const CONFIG_PATH = path.join(PROJECT_ROOT, "config.yaml");

function safePath(p: string): string {
  return p.replace(/\\/g, "\\\\").replace(/"/g, '\\"');
}

// GET /api/config
export async function GET() {
  const result = spawnSync("python3", [
    "-c",
    `import yaml, json, sys
with open("${safePath(CONFIG_PATH)}") as f:
    cfg = yaml.safe_load(f)
print(json.dumps(cfg, indent=2))`,
  ], { cwd: PROJECT_ROOT, encoding: "utf-8" });

  if (result.error) {
    return Response.json({ error: result.error.message }, { status: 500 });
  }
  try {
    const cfg = JSON.parse(result.stdout);
    return Response.json(cfg);
  } catch {
    return Response.json({ error: "Failed to parse config", stderr: result.stderr }, { status: 500 });
  }
}

// PUT /api/config — update config.yaml
export async function PUT(req: NextRequest) {
  const updates = await req.json();
  const updatesJson = JSON.stringify(updates);

  const result = spawnSync("python3", [
    "-c",
    `import yaml, json, sys
import os

with open("${safePath(CONFIG_PATH)}") as f:
    cfg = yaml.safe_load(f) or {}

updates_raw = sys.argv[1]
try:
    updates = json.loads(updates_raw)
except json.JSONDecodeError:
    print(json.dumps({"error": "invalid json"}))
    sys.exit(1)

def deep_merge(base, overrides):
    for k, v in overrides.items():
        if isinstance(v, dict) and k in base and isinstance(base[k], dict):
            deep_merge(base[k], v)
        else:
            base[k] = v

deep_merge(cfg, updates)

with open("${safePath(CONFIG_PATH)}", "w") as f:
    yaml.dump(cfg, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

print(json.dumps({"ok": True, "config": cfg}))`,
    updatesJson,
  ], { cwd: PROJECT_ROOT, encoding: "utf-8" });

  if (result.error) {
    return Response.json({ error: result.error.message }, { status: 500 });
  }
  try {
    const out = JSON.parse(result.stdout);
    return Response.json(out);
  } catch {
    return Response.json({ error: result.stderr || "Failed to update config" }, { status: 500 });
  }
}
