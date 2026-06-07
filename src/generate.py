"""
圖片生成模組 — 支援 OpenAI / Stability / Replicate / Local / Dummy
"""
from __future__ import annotations

import io
import json
import os
import subprocess
import struct
import time
import zlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

import requests
from PIL import Image, ImageDraw

from .config import get_config


class ImageGenerator(ABC):
    def generate(self, prompt: str, output_path: str) -> str:
        path = self._generate_impl(prompt, output_path)
        
        # Auto upscale to meet stock agency requirements (min 4MP, target 6MP)
        from .image_utils import upscale_image_to_mp
        upscale_image_to_mp(path, target_mp=6.0, quality=get_config().output.quality)
        return path

    @abstractmethod
    def _generate_impl(self, prompt: str, output_path: str) -> str:
        ...


class OpenAIGenerator(ImageGenerator):
    def _generate_impl(self, prompt: str, output_path: str) -> str:
        cfg = get_config().generation.openai
        api_key = cfg.api_key or os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")

        resp = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": cfg.model,
                "prompt": prompt,
                "n": cfg.n,
                "size": cfg.size,
                "quality": cfg.quality,
                "response_format": "b64_json",
            },
            timeout=120,
        )
        resp.raise_for_status()
        img_data = resp.json()["data"][0]["b64_json"]
        img = Image.open(io.BytesIO(__import__("base64").b64decode(img_data)))
        if img.mode != "RGB":
            img = img.convert("RGB")
        img.save(output_path, "JPEG", quality=get_config().output.quality)
        return output_path


class StabilityGenerator(ImageGenerator):
    def _generate_impl(self, prompt: str, output_path: str) -> str:
        cfg = get_config().generation.stability
        api_key = cfg.api_key or os.getenv("STABILITY_API_KEY", "")
        if not api_key:
            raise ValueError("STABILITY_API_KEY not set")
        resp = requests.post(
            "https://api.stability.ai/v2beta/stable-image/generate/sd3",
            headers={"Authorization": f"Bearer {api_key}", "Accept": "image/*"},
            files={"none": ""},
            data={"prompt": prompt, "output_format": "jpeg", "model": cfg.model,
                  "width": cfg.width, "height": cfg.height, "steps": cfg.steps, "mode": "text-to-image"},
            timeout=120,
        )
        resp.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(resp.content)
        return output_path


class ReplicateGenerator(ImageGenerator):
    def _generate_impl(self, prompt: str, output_path: str) -> str:
        cfg = get_config().generation.replicate
        token = cfg.api_token or os.getenv("REPLICATE_API_TOKEN", "")
        if not token:
            raise ValueError("REPLICATE_API_TOKEN not set")
        resp = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Prefer": "wait"},
            json={"version": cfg.model, "input": {"prompt": prompt, "num_outputs": 1}},
            timeout=120,
        )
        resp.raise_for_status()
        pred = resp.json()
        while pred["status"] not in ("succeeded", "failed", "canceled"):
            time.sleep(2)
            resp = requests.get(f"https://api.replicate.com/v1/predictions/{pred['id']}",
                                headers={"Authorization": f"Bearer {token}"}, timeout=30)
            resp.raise_for_status()
            pred = resp.json()
        if pred["status"] != "succeeded":
            raise RuntimeError(f"Replicate failed: {pred.get('error', 'unknown')}")
        img_resp = requests.get(pred["output"][0], timeout=60)
        with open(output_path, "wb") as f:
            f.write(img_resp.content)
        return output_path


class LocalGenerator(ImageGenerator):
    _pipeline = None

    def _generate_impl(self, prompt: str, output_path: str) -> str:
        cfg = get_config().generation.local
        try:
            import torch
            from diffusers import StableDiffusion3Pipeline
        except ImportError:
            raise ImportError("Requires: pip install diffusers torch transformers accelerate")
        
        if LocalGenerator._pipeline is None:
            pipe = StableDiffusion3Pipeline.from_pretrained(
                cfg.model_id, torch_dtype=torch.float16 if cfg.device == "cuda" else torch.float32)
            pipe.to(cfg.device)
            LocalGenerator._pipeline = pipe
        else:
            pipe = LocalGenerator._pipeline
            
        image = pipe(prompt=prompt, width=cfg.width, height=cfg.height, num_inference_steps=28).images[0]
        if image.mode != "RGB":
            image = image.convert("RGB")
        image.save(output_path, "JPEG", quality=get_config().output.quality)
        return output_path


class DummyGenerator(ImageGenerator):
    """
    測試用：不用 API，直接生成漸層色 JPEG 圖片。
    讓使用者在沒有 API key 的情況下也能測試整個 pipeline。
    """
    def _generate_impl(self, prompt: str, output_path: str) -> str:
        width, height = 2400, 1600  # 4MP minimum
        img = Image.new("RGB", (width, height), color=(30, 40, 60))
        draw = ImageDraw.Draw(img)

        # Draw a simple gradient based on prompt hash
        h = hash(prompt) & 0xFFFFFF
        r1, g1, b1 = (h >> 16) & 0xFF, (h >> 8) & 0xFF, h & 0xFF
        r2, g2, b2 = 255 - r1, 255 - g1, 255 - b1

        for y in range(height):
            ratio = y / height
            r = int(r1 * (1 - ratio) + r2 * ratio)
            g = int(g1 * (1 - ratio) + g2 * ratio)
            b = int(b1 * (1 - ratio) + b2 * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # Draw some shapes to make it less boring
        import random
        rng = random.Random(h)
        for _ in range(20):
            x1 = rng.randint(0, width - 1)
            y1 = rng.randint(0, height - 1)
            x2 = rng.randint(0, width - 1)
            y2 = rng.randint(0, height - 1)
            # Ensure x1 <= x2, y1 <= y2
            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y1, y2)
            color = (rng.randint(0, 255), rng.randint(0, 255), rng.randint(0, 255))
            draw.ellipse([x1, y1, x2, y2], fill=color, outline=None)

        img.save(output_path, "JPEG", quality=get_config().output.quality)
        print(f"  [dummy] Generated test image: {Path(output_path).name}")
        return output_path


class ChatGPTWebGenGenerator(ImageGenerator):
    """
    使用 lunkerchen/chatgpt-web-gen 的本機 CLI，透過 ChatGPT Web 生圖。
    需先在該專案執行 `python gen.py --login` 建立 cookies.json。
    """
    def _generate_impl(self, prompt: str, output_path: str) -> str:
        project_dir = Path(
            os.getenv("CHATGPT_WEB_GEN_DIR", "/Users/lunker/Developer/Projects/chatgpt-web-gen")
        )
        script = project_dir / "gen.py"
        if not script.exists():
            raise FileNotFoundError(f"chatgpt-web-gen not found: {script}")

        proc = subprocess.run(
            ["python3", str(script), prompt],
            cwd=project_dir,
            text=True,
            capture_output=True,
            timeout=210,
            check=False,
        )
        if proc.returncode != 0:
            msg = (proc.stderr or proc.stdout).strip()
            raise RuntimeError(f"chatgpt-web-gen failed: {msg}")

        image_path = None
        for line in proc.stdout.splitlines():
            if line.startswith("IMAGE:"):
                image_path = Path(line.removeprefix("IMAGE:").strip())
                break
        if not image_path or not image_path.exists():
            raise RuntimeError("chatgpt-web-gen did not return an IMAGE path")

        img = Image.open(image_path)
        if img.mode != "RGB":
            img = img.convert("RGB")
        img.save(output_path, "JPEG", quality=get_config().output.quality)
        return output_path


class BaoyuImagineGenerator(ImageGenerator):
    """
    使用 baoyu-imagine (bun script) 透過多平台 API 生圖。
    支援 OpenAI GPT Image、Google Gemini、DashScope、MiniMax 等。
    需設定對應的 API key 環境變數。
    """
    def _generate_impl(self, prompt: str, output_path: str) -> str:
        import shutil
        script = Path(
            os.getenv("BAOYU_IMAGINE_SCRIPT",
                      os.path.expanduser("~/.agents/skills/baoyu-imagine/scripts/main.ts"))
        )
        if not script.exists():
            raise FileNotFoundError(f"baoyu-imagine not found: {script}")

        bun = shutil.which("bun") or "/opt/homebrew/bin/bun"

        cfg = get_config().generation
        args = [
            bun, str(script),
            "--prompt", prompt,
            "--image", output_path,
        ]

        # Optional overrides from config or env
        sub_provider = os.getenv("BAOYU_IMAGINE_PROVIDER", "")
        sub_model = os.getenv("BAOYU_IMAGINE_MODEL", "")
        if sub_provider:
            args += ["--provider", sub_provider]
        if sub_model:
            args += ["--model", sub_model]

        proc = subprocess.run(
            args,
            text=True,
            capture_output=True,
            timeout=210,
            check=False,
        )
        if proc.returncode != 0:
            msg = (proc.stderr or "unknown error").strip()
            raise RuntimeError(f"baoyu-imagine failed: {msg}")

        out_p = Path(output_path)
        if not out_p.exists():
            raise RuntimeError(f"baoyu-imagine did not produce output: {output_path}")

        img = Image.open(out_p)
        if img.mode != "RGB":
            img = img.convert("RGB")
        img.save(output_path, "JPEG", quality=get_config().output.quality)
        return output_path


# ── Factory ────────────────────────────────────────────────

GENERATORS: dict[str, type[ImageGenerator]] = {
    "openai": OpenAIGenerator,
    "stability": StabilityGenerator,
    "replicate": ReplicateGenerator,
    "local": LocalGenerator,
    "dummy": DummyGenerator,
    "chatgpt-web-gen": ChatGPTWebGenGenerator,
    "baoyu-imagine": BaoyuImagineGenerator,
}


def get_generator(provider: str | None = None) -> ImageGenerator:
    if provider is None:
        provider = get_config().generation.provider
    cls = GENERATORS.get(provider)
    if not cls:
        raise ValueError(f"Unknown provider: {provider}. Choose: {list(GENERATORS.keys())}")
    return cls()
