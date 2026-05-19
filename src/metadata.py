"""
Metadata 產生器 — Adobe Stock 專用標題、關鍵詞、分類
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Optional

import requests
from rich.console import Console

from .config import get_config

console = Console()

# ── Adobe Stock 分類 ──────────────────────────────────────
# 對應 contributor.stock.adobe.com 上的類別下拉選單
CATEGORIES = {
    "3d-renders": "3D Renders",
    "abstract": "Abstract",
    "animals": "Animals",
    "buildings-landmarks": "Buildings/Landmarks",
    "business-finance": "Business/Finance",
    "education": "Education",
    "food-drink": "Food & Drink",
    "healthcare-medical": "Healthcare/Medical",
    "holidays": "Holidays",
    "industrial": "Industrial",
    "illustrations-vectors": "Illustrations/Vectors",
    "nature": "Nature",
    "objects": "Objects",
    "people": "People",
    "religious": "Religious",
    "science": "Science",
    "signs-symbols": "Signs/Symbols",
    "sports-fitness": "Sports & Fitness",
    "technology": "Technology",
    "travel": "Travel",
    "vintage": "Vintage",
}


class ImageMetadata:
    def __init__(
        self,
        filename: str,
        title: str = "",
        description: str = "",
        keywords: list[str] | None = None,
        category: str = "",
        ai_generated: bool = True,
        has_releases: bool = False,
    ):
        self.filename = filename
        self.title = title
        self.description = description
        self.keywords = keywords or []
        self.category = category
        self.ai_generated = ai_generated
        self.has_releases = has_releases


class MetadataGenerator:
    """
    LLM-based metadata generation for Adobe Stock.

    Adobe Stock requirements:
    - Title: max 200 chars, descriptive, English
    - Keywords: min 7, max 50, comma-separated
    - Category: pick from predefined list
    - AI generated: must be flagged (Adobe accepts this)
    """

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model

    def generate(self, prompt: str, filename: str) -> ImageMetadata:
        if self.api_key:
            return self._with_llm(prompt, filename)
        return self._heuristic(prompt, filename)

    def _with_llm(self, prompt: str, filename: str) -> ImageMetadata:
        system = """You are an Adobe Stock metadata expert. Generate metadata for stock photos.

Rules for Adobe Stock:
- Title: max 200 chars, descriptive sentence, English, factual
- Keywords: 15-30 relevant keywords, comma-separated, English, from general to specific
- Category: pick best match from: abstract, animals, buildings-landmarks, business-finance, education, food-drink, healthcare-medical, holidays, industrial, illustrations-vectors, nature, objects, people, religious, science, signs-symbols, sports-fitness, technology, travel, vintage
- Generative AI: defaults to true — mark as AI-generated since we're using AI generation
- No hype words ("stunning", "amazing"), describe what's actually in the image

Respond in JSON:
{
  "title": "...",
  "description": "...",
  "keywords": ["kw1", "kw2", ...],
  "category": "technology",
  "ai_generated": true,
  "has_releases": false
}"""

        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": f"Generate Adobe Stock metadata for: {prompt}"},
                ],
                "temperature": 0.3,
                "response_format": {"type": "json_object"},
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()["choices"][0]["message"]["content"]
        parsed = json.loads(data)

        cfg = get_config().metadata
        return ImageMetadata(
            filename=filename,
            title=parsed["title"][:200],
            description=parsed.get("description", parsed["title"])[:200],
            keywords=parsed["keywords"][:cfg.max_keywords],
            category=parsed.get("category", cfg.category or ""),
            ai_generated=parsed.get("ai_generated", cfg.ai_generated),
            has_releases=parsed.get("has_releases", cfg.has_releases),
        )

    def _heuristic(self, prompt: str, filename: str) -> ImageMetadata:
        words = prompt.lower().split()
        stopwords = {"a", "an", "the", "in", "on", "at", "of", "for", "with", "and", "or"}
        keywords = [w.strip(".,;:!?") for w in words if w not in stopwords and len(w) > 2]
        seen = set()
        unique_kw = []
        for k in keywords:
            if k not in seen:
                seen.add(k)
                unique_kw.append(k)

        title = prompt.strip().rstrip(".,")
        if not title.endswith("."):
            title += "."

        cfg = get_config().metadata
        return ImageMetadata(
            filename=filename,
            title=title.capitalize(),
            description=title,
            keywords=unique_kw[:cfg.max_keywords],
            category=cfg.category or "",
            ai_generated=cfg.ai_generated,
            has_releases=cfg.has_releases,
        )


# ── CSV 輸出 (Adobe Stock 格式) ──────────────────────────


def metadata_to_csv_row(meta: ImageMetadata) -> list[str]:
    kw_str = ", ".join(meta.keywords)
    return [
        meta.filename,
        meta.title,
        meta.description,
        kw_str,
        meta.category,
        "Y" if meta.ai_generated else "N",
        "Y" if meta.has_releases else "N",
    ]


def write_metadata_csv(metadata_list: list[ImageMetadata], output_path: str):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Filename",
            "Title",
            "Description",
            "Keywords",
            "Category",
            "AI Generated",
            "Has Releases",
        ])
        for meta in metadata_list:
            writer.writerow(metadata_to_csv_row(meta))
    console.print(f"[green]✓[/green] Metadata CSV: {output_path}")
