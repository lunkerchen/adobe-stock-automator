"""
Adobe Stock Automator — 設定載入
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel


# ── Config models ──────────────────────────────────────────

class OpenAIConfig(BaseModel):
    api_key: str = ""
    model: str = "dall-e-3"
    size: str = "1792x1024"
    quality: str = "standard"
    n: int = 1


class StabilityConfig(BaseModel):
    api_key: str = ""
    model: str = "stable-diffusion-3-5-large"
    width: int = 2048
    height: int = 2048
    steps: int = 40


class ReplicateConfig(BaseModel):
    api_token: str = ""
    model: str = "stability-ai/stable-diffusion-3.5"


class LocalConfig(BaseModel):
    model_id: str = "stabilityai/stable-diffusion-3-5-large-turbo"
    device: str = "mps"
    width: int = 1024
    height: int = 1024


class GenerationConfig(BaseModel):
    provider: str = "openai"
    openai: OpenAIConfig = OpenAIConfig()
    stability: StabilityConfig = StabilityConfig()
    replicate: ReplicateConfig = ReplicateConfig()
    local: LocalConfig = LocalConfig()


class OutputConfig(BaseModel):
    dir: str = "./output"
    prefix: str = "ads_"
    quality: int = 95


class MetadataConfig(BaseModel):
    language: str = "en"
    min_keywords: int = 7
    max_keywords: int = 50
    category: Optional[str] = None
    ai_generated: bool = True
    has_releases: bool = False


class FTPConfig(BaseModel):
    host: str = "ftp.contributor.stock.adobe.com"
    port: int = 21


class AdobeContributorConfig(BaseModel):
    email: str = ""
    password: str = ""


class AdobeConfig(BaseModel):
    contributor: AdobeContributorConfig = AdobeContributorConfig()
    ftp: FTPConfig = FTPConfig()


class UploadConfig(BaseModel):
    mode: str = "ftp"
    ftp_upload: bool = True
    generate_csv: bool = True
    csv_path: str = "./output/metadata.csv"


class BrowserConfig(BaseModel):
    headless: bool = False
    slow_mo: int = 800
    cookie_cache: str = "./.cookies/adobe_stock.json"
    submit_url: str = "https://contributor.stock.adobe.com/en/uploads"


class PixtaContributorConfig(BaseModel):
    email: str = ""
    password: str = ""


class PixtaConfig(BaseModel):
    contributor: PixtaContributorConfig = PixtaContributorConfig()


class CloakConfig(BaseModel):
    """CloakBrowser upload configuration (supports multiple platforms)."""
    platform: str = "pixta"  # pixta | adobe-stock
    headless: bool = False
    slow_mo: int = 500
    humanize: bool = True


class Config(BaseModel):
    adobe: AdobeConfig = AdobeConfig()
    pixta: PixtaConfig = PixtaConfig()
    generation: GenerationConfig = GenerationConfig()
    output: OutputConfig = OutputConfig()
    metadata: MetadataConfig = MetadataConfig()
    upload: UploadConfig = UploadConfig()
    browser: BrowserConfig = BrowserConfig()
    cloak: CloakConfig = CloakConfig()


# ── Loader ─────────────────────────────────────────────────

_CONFIG: Config | None = None


def load_config(path: str = "config.yaml") -> Config:
    global _CONFIG
    _load_dotenv(".env")

    raw = {}
    config_path = Path(path)
    if config_path.exists():
        raw = yaml.safe_load(config_path.read_text()) or {}

    cfg = Config(**raw)

    # Env overrides
    if os.getenv("OPENAI_API_KEY"):
        cfg.generation.openai.api_key = os.getenv("OPENAI_API_KEY", "")
    if os.getenv("STABILITY_API_KEY"):
        cfg.generation.stability.api_key = os.getenv("STABILITY_API_KEY", "")
    if os.getenv("REPLICATE_API_TOKEN"):
        cfg.generation.replicate.api_token = os.getenv("REPLICATE_API_TOKEN", "")
    if os.getenv("ADOBE_STOCK_EMAIL"):
        cfg.adobe.contributor.email = os.getenv("ADOBE_STOCK_EMAIL", "")
    if os.getenv("ADOBE_STOCK_PASSWORD"):
        cfg.adobe.contributor.password = os.getenv("ADOBE_STOCK_PASSWORD", "")
    if os.getenv("PIXTA_EMAIL"):
        cfg.pixta.contributor.email = os.getenv("PIXTA_EMAIL", "")
    if os.getenv("PIXTA_PASSWORD"):
        cfg.pixta.contributor.password = os.getenv("PIXTA_PASSWORD", "")

    _CONFIG = cfg
    return cfg


def _load_dotenv(path: str = ".env"):
    if Path(path).exists():
        load_dotenv(path)


def get_config() -> Config:
    assert _CONFIG is not None, "Config not loaded. Call load_config() first."
    return _CONFIG
