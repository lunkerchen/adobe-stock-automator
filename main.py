#!/usr/bin/env python3
"""
Adobe Stock Automator — CLI 主入口

自動生成圖片 → FTP 上傳 → Metadata CSV / Browser 提交
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel

from src.config import load_config, get_config
from src.generate import get_generator
from src.upload import ftp_upload_all
from src.metadata import MetadataGenerator, write_metadata_csv
from src.upload_cloak import CloakUploader, PLATFORMS

console = Console()

BANNER = """
╔══════════════════════════════════════════════╗
║        Adobe Stock Automator v0.1           ║
║    Generate → Upload → Submit to Adobe Stock║
╚══════════════════════════════════════════════╝
"""


@click.group()
@click.option("--config", "-c", default="config.yaml", help="Config file")
@click.version_option(version="0.1.0")
def cli(config: str):
    """Adobe Stock Automator — 自動生成圖片並上傳到 Adobe Stock"""
    load_config(config)
    console.print(BANNER)

    cfg = get_config()
    if cfg.metadata.ai_generated:
        console.print(
            Panel(
                "[green]✓ Adobe Stock 接受 AI 生成內容[/green]\n"
                "只需在提交時標示「Generative AI」即可。\n"
                "本工具會自動處理這個標示。",
                border_style="green",
            )
        )


def get_model_name(provider: str | None) -> str:
    cfg = get_config()
    prov = provider or cfg.generation.provider
    if prov == "openai":
        return cfg.generation.openai.model
    elif prov == "stability":
        return cfg.generation.stability.model
    elif prov == "replicate":
        return cfg.generation.replicate.model
    elif prov == "local":
        return cfg.generation.local.model_id.split("/")[-1]
    elif prov == "dummy":
        return "Dummy Generator"
    return "AI Generator"


@cli.command()
@click.argument("prompt")
@click.option("--count", "-n", default=1, help="Number of images to generate")
@click.option("--output", "-o", default=None, help="Output directory")
@click.option("--provider", "-p", default=None, help="Generation provider")
@click.option("--no-upload", is_flag=True, help="Skip FTP upload")
@click.option("--no-csv", is_flag=True, help="Skip CSV metadata")
@click.option("--submit/--no-submit", default=True, help="Use browser to upload + auto-fill metadata (default: on)")
@click.option("--ai-key", default=None, help="OpenAI API key for metadata")
@click.option("--freepik", is_flag=True, help="Upload and export CSV for Freepik")
def generate(
    prompt: str,
    count: int,
    output: Optional[str],
    provider: Optional[str],
    no_upload: bool,
    no_csv: bool,
    submit: bool,
    ai_key: Optional[str],
    freepik: bool,
):
    """
    生成圖片 → Browser 上傳 + 自動填寫 Metadata

    PROMPT: 圖片的文字描述

    流程:
    1. 用 AI 生成圖片 (支援 dummy 模式免 API key)
    2. 產出 CSV metadata (可選 Adobe / Freepik 格式)
    3. 自動上傳檔案至 Freepik FTP（如果啟用 --freepik）
    4. 開啟瀏覽器登入 Adobe Stock Contributor
    5. 自動上傳檔案 + 填寫 title/keywords/AI 標籤
    6. 你自己在瀏覽器點 Submit All
    """
    cfg = get_config()
    output_dir = Path(output or cfg.output.dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── 1. Generate images ──
    generator = get_generator(provider)
    console.print(f"\n[bold]Generating {count}x images...[/bold]")
    console.print(f"  Provider: {provider or cfg.generation.provider}")
    console.print(f"  Prompt: {prompt[:80]}...\n")

    image_paths = []
    metadata_list = []
    meta_gen = MetadataGenerator(api_key=ai_key or cfg.generation.openai.api_key)
    model_name = get_model_name(provider)

    for i in range(count):
        ts = int(time.time() * 1000)
        filename = f"{cfg.output.prefix}{ts}_{i}.jpg"
        filepath = str(output_dir / filename)

        try:
            generator.generate(prompt, filepath)
            image_paths.append(filepath)
            meta = meta_gen.generate(prompt, filename, model_name=model_name)
            metadata_list.append(meta)
            console.print(f"  [green]✓[/green] {filename}")
        except Exception as e:
            console.print(f"  [red]✗[/red] Image {i+1}: {e}")

    if not image_paths:
        console.print("[red]No images generated. Aborting.[/red]")
        sys.exit(1)

    console.print(f"\n[bold]Generated: {len(image_paths)} images[/bold]")
    console.print(f"  Output: {output_dir.resolve()}")

    # ── 2. Write CSV ──
    if not no_csv:
        csv_path = output_dir / "metadata.csv"
        write_metadata_csv(metadata_list, str(csv_path))
        if freepik:
            from src.metadata import write_freepik_csv
            freepik_csv = output_dir / "metadata_freepik.csv"
            write_freepik_csv(metadata_list, str(freepik_csv))

    # ── 3. FTP Upload ──
    if not no_upload:
        ftp_upload_all(image_paths, platform="adobe-stock")
        if freepik:
            ftp_upload_all(image_paths, platform="freepik")

    # ── 4. Browser submit (default on) ──
    if submit:
        console.print("\n[bold]Launching browser for upload + metadata submission...[/bold]")
        try:
            import asyncio
            from src.submit_browser import AdobeStockBrowserSubmitter

            async def _run():
                async with AdobeStockBrowserSubmitter() as submitter:
                    return await submitter.run(metadata_list, image_paths if not no_upload else None)

            asyncio.run(_run())
        except Exception as e:
            console.print(f"[red]Browser submission error: {e}[/red]")
            console.print("[yellow]Fallback: CSV is available for manual import.[/yellow]")

    # ── Summary ──
    console.print(f"\n[bold green]✓ Done![/bold green]")
    console.print("\n[bold]Next steps:[/bold]")
    console.print("  1. Go to https://contributor.stock.adobe.com/en/uploads")
    console.print("  2. Review your files (they appear after FTP upload)")
    console.print("  3. If using CSV: use 'Import CSV' if available, or use --submit")
    console.print("  4. Click 'Submit All' to send for review")


@cli.command()
@click.argument("batch_file", type=click.Path(exists=True))
@click.option("--count", "-n", default=1, help="Images per prompt")
@click.option("--no-upload", is_flag=True)
@click.option("--submit", is_flag=True)
@click.option("--freepik", is_flag=True, help="Upload and export CSV for Freepik")
def batch(batch_file: str, count: int, no_upload: bool, submit: bool, freepik: bool):
    """Batch process: one prompt per line in text file."""
    prompts = Path(batch_file).read_text().strip().splitlines()
    prompts = [p.strip() for p in prompts if p.strip()]

    cfg = get_config()
    output_dir = Path(cfg.output.dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    generator = get_generator()
    meta_gen = MetadataGenerator(api_key=cfg.generation.openai.api_key)
    model_name = get_model_name(cfg.generation.provider)

    all_paths = []
    all_metadata = []

    for idx, prompt in enumerate(prompts):
        console.print(f"\n[bold](#{idx+1})[/bold] {prompt[:80]}")
        for i in range(count):
            ts = int(time.time() * 1000)
            filename = f"{cfg.output.prefix}{ts}_{idx}_{i}.jpg"
            filepath = str(output_dir / filename)
            try:
                generator.generate(prompt, filepath)
                all_paths.append(filepath)
                all_metadata.append(meta_gen.generate(prompt, filename, model_name=model_name))
                console.print(f"  [green]✓[/green] {filename}")
            except Exception as e:
                console.print(f"  [red]✗[/red] {e}")

    write_metadata_csv(all_metadata, str(output_dir / "metadata.csv"))
    if freepik:
        from src.metadata import write_freepik_csv
        write_freepik_csv(all_metadata, str(output_dir / "metadata_freepik.csv"))

    if not no_upload and all_paths:
        ftp_upload_all(all_paths, platform="adobe-stock")
        if freepik:
            ftp_upload_all(all_paths, platform="freepik")

    if submit:
        import asyncio
        from src.submit_browser import AdobeStockBrowserSubmitter

        async def _run():
            async with AdobeStockBrowserSubmitter() as sb:
                await sb.run(all_metadata, all_paths if not no_upload else None)

        asyncio.run(_run())

    console.print(f"\n[bold green]Batch complete: {len(all_paths)} images[/bold green]")


@cli.command()
@click.argument("prompt")
@click.option("--count", "-n", default=1, help="Number of images to generate")
@click.option("--output", "-o", default=None, help="Output directory")
@click.option("--provider", "-p", default=None, help="Generation provider")
@click.option("--platform", "--pl", default=None, help="Target platform (pixta, adobe-stock)")
@click.option("--ai-key", default=None, help="API key for metadata generation")
@click.option("--headless", is_flag=True, help="Run CloakBrowser headless")
@click.option("--skip-upload", is_flag=True, help="Skip upload, just login + metadata")
@click.option("--skip-metadata", is_flag=True, help="Skip metadata fill")
@click.option("--email", default=None, help="Platform login email")
@click.option("--password", default=None, help="Platform login password")
def cloak(
    prompt: str,
    count: int,
    output: Optional[str],
    provider: Optional[str],
    platform: Optional[str],
    ai_key: Optional[str],
    headless: bool,
    skip_upload: bool,
    skip_metadata: bool,
    email: Optional[str],
    password: Optional[str],
):
    """
    使用 CloakBrowser 生成圖片並上傳到圖庫平台（PIXTA / Adobe Stock）。

    PROMPT: 圖片的文字描述

    流程:
    1. 用 AI 生成圖片（或 --provider dummy 免 API key）
    2. 開啟 CloakBrowser（stealth Chromium）
    3. 登入平台（支援 cookie 持久化 + 手動 2FA）
    4. 上傳檔案（自動或手動拖曳）
    5. 填寫 Metadata（title, keywords, AI 標籤）
    6. 你確認後手動點 Submit
    """
    cfg = get_config()
    output_dir = Path(output or cfg.output.dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Resolve platform
    plat = platform or cfg.cloak.platform
    if plat not in PLATFORMS:
        console.print(f"[red]Unknown platform: {plat}. Choose: {list(PLATFORMS.keys())}[/red]")
        sys.exit(1)

    # Resolve credentials
    if plat == "pixta":
        cred_email = email or cfg.pixta.contributor.email
        cred_password = password or cfg.pixta.contributor.password
    elif plat == "adobe-stock":
        cred_email = email or cfg.adobe.contributor.email
        cred_password = password or cfg.adobe.contributor.password
    else:
        cred_email = email or ""
        cred_password = password or ""

    # ── 1. Generate images ──
    generator = get_generator(provider)
    console.print(f"\n[bold]Generating {count}x images...[/bold]")
    console.print(f"  Provider: {provider or cfg.generation.provider}")
    console.print(f"  Platform: {plat}")
    console.print(f"  Prompt: {prompt[:80]}...\n")

    image_paths = []
    metadata_list = []
    meta_gen = MetadataGenerator(api_key=ai_key or cfg.generation.openai.api_key)

    for i in range(count):
        ts = int(time.time() * 1000)
        filename = f"{cfg.output.prefix}{ts}_{i}.jpg"
        filepath = str(output_dir / filename)
        try:
            generator.generate(prompt, filepath)
            image_paths.append(filepath)
            meta = meta_gen.generate(prompt, filename)
            metadata_list.append(meta)
            console.print(f"  [green]✓[/green] {filename}")
        except Exception as e:
            console.print(f"  [red]✗[/red] Image {i+1}: {e}")

    if not image_paths:
        console.print("[red]No images generated. Aborting.[/red]")
        sys.exit(1)

    # Write CSV as fallback
    csv_path = output_dir / "metadata.csv"
    write_metadata_csv(metadata_list, str(csv_path))

    # ── 2. CloakBrowser upload pipeline ──
    console.print(f"\n[bold]Launching CloakBrowser for {plat}...[/bold]")

    try:
        with CloakUploader(
            platform=plat,
            headless=headless or cfg.cloak.headless,
            slow_mo=cfg.cloak.slow_mo,
            humanize=cfg.cloak.humanize,
        ) as uploader:
            uploader.run(
                metadata_list=metadata_list,
                file_paths=image_paths if not skip_upload else None,
                email=cred_email,
                password=cred_password,
                skip_upload=skip_upload,
                skip_metadata=skip_metadata,
            )
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user.[/yellow]")
    except Exception as e:
        console.print(f"[red]CloakBrowser error: {e}[/red]")
        console.print("[yellow]Fallback: CSV is available for manual import.[/yellow]")
        import traceback
        console.print(traceback.format_exc())


@cli.command()
@click.argument("prompt")
@click.option("--count", "-n", default=1, help="Number of images to generate")
@click.option("--output", "-o", default=None, help="Output directory")
@click.option("--provider", "-p", default=None, help="Generation provider")
@click.option("--ai-key", default=None, help="OpenAI API key for metadata")
@click.option("--email", default=None, help="Adobe Stock login email")
@click.option("--password", default=None, help="Adobe Stock login password")
@click.option("--headless", is_flag=True, help="Run browser headless (no visible window)")
@click.option("--skip-upload", is_flag=True, help="Skip file upload, only fill metadata")
@click.option("--skip-metadata", is_flag=True, help="Skip metadata fill, only upload")
def portal_upload(
    prompt: str,
    count: int,
    output: Optional[str],
    provider: Optional[str],
    ai_key: Optional[str],
    email: Optional[str],
    password: Optional[str],
    headless: bool,
    skip_upload: bool,
    skip_metadata: bool,
):
    """
    使用 Adobe Stock Contributor Portal 上傳輔助模組：

    自動生成圖片 → 瀏覽器登入 → 上傳檔案 → 填入 metadata + AI 標記 → 你確認後手動提交。

    PROMPT: 圖片的文字描述

    流程:
    1. 用 AI 生成圖片（支援 --provider dummy 免 API key）
    2. 產出 metadata（title / keywords / AI 標記）
    3. 開啟瀏覽器前往 contributor.stock.adobe.com
    4. 登入（支援 cookie 持久化 + 手動 2FA）
    5. 上傳檔案 + 自動填寫 metadata + AI 標記
    6. 你確認無誤後在瀏覽器點 Submit All
    """
    from src.portal_upload import AdobePortalUpload

    cfg = get_config()
    output_dir = Path(output or cfg.output.dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── 1. Generate images ──
    generator = get_generator(provider)
    console.print(f"\n[bold]Generating {count}x images...[/bold]")
    console.print(f"  Provider: {provider or cfg.generation.provider}")
    console.print(f"  Prompt: {prompt[:80]}...\n")

    image_paths = []
    metadata_list = []
    meta_gen = MetadataGenerator(api_key=ai_key or cfg.generation.openai.api_key)

    for i in range(count):
        ts = int(time.time() * 1000)
        filename = f"{cfg.output.prefix}{ts}_{i}.jpg"
        filepath = str(output_dir / filename)
        try:
            generator.generate(prompt, filepath)
            image_paths.append(filepath)
            meta = meta_gen.generate(prompt, filename)
            metadata_list.append(meta)
            console.print(f"  [green]✓[/green] {filename}")
        except Exception as e:
            console.print(f"  [red]✗[/red] Image {i+1}: {e}")

    if not image_paths:
        console.print("[red]No images generated. Aborting.[/red]")
        sys.exit(1)

    # Write CSV as fallback
    from src.metadata import write_metadata_csv
    csv_path = output_dir / "metadata.csv"
    write_metadata_csv(metadata_list, str(csv_path))

    # ── 2. Portal upload pipeline ──
    console.print(f"\n[bold]Launching Adobe Stock Contributor Portal...[/bold]")

    try:
        with AdobePortalUpload(headless=headless) as portal:
            result = portal.run(
                metadata_list=metadata_list,
                file_paths=image_paths if not skip_upload else None,
                email=email or "",
                password=password or "",
                skip_upload=skip_upload,
                skip_metadata=skip_metadata,
            )
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user.[/yellow]")
    except Exception as e:
        console.print(f"[red]Portal upload error: {e}[/red]")
        console.print("[yellow]Fallback: CSV metadata is available at output/metadata.csv[/yellow]")
        import traceback
        console.print(traceback.format_exc())


@cli.command()
@click.option("--platform", default=None, help="Show requirements for a specific platform")
def requirements(platform: Optional[str]):
    """Show image requirements for stock platforms."""
    if platform and platform == "pixta":
        console.print(Panel.fit(
            "[bold]PIXTA Image Requirements[/bold]\n\n"
            "  Resolution:  min 3 MP\n"
            "  Format:      JPEG, PNG\n"
            "  Max size:    30 MB\n"
            "  Title:       max 100 chars (Japanese)\n"
            "  Keywords:    min 5, max 20 (Japanese)\n"
            "  AI content:  ✅ Accepted (must tag)\n\n"
            "[bold]Upload:[/bold] Web browser only (no FTP)\n"
            "  https://pixta.jp/contributor/upload/\n\n"
            "[bold]Authentication:[/bold]\n"
            "  PIXTA account login (may need email verification)\n"
            "  Use: python3 main.py cloak \"prompt\" --platform pixta",
            border_style="cyan",
        ))
        return

    console.print(Panel.fit(
        "[bold]Adobe Stock Image Requirements[/bold]\n\n"
        "  Resolution:  min 4 MP (e.g. 2400×1600)\n"
        "  Format:      JPEG (sRGB)\n"
        "  Max size:    50 MB (web)\n"
        "  Title:       max 200 chars\n"
        "  Keywords:    min 7 (English)\n\n"
        "[bold]Upload Methods:[/bold]\n"
        "  • Web Browser:  https://contributor.stock.adobe.com/en/uploads\n"
        "  • FTP:          ftp.adobe.com (deprecated, may not work)\n"
        "  • API:          No public contributor API\n\n"
        "[bold]AI-generated content:[/bold]\n"
        "  ACCEPTED by Adobe Stock!\n"
        "  Must be tagged as 'Generative AI' on submission.\n"
        "  This tool handles the tagging automatically.\n\n"
        "[bold]Authentication:[/bold]\n"
        "  Adobe ID login may require email verification code.\n"
        "  Use: python3 main.py cloak \"prompt\" --platform adobe-stock",
        border_style="cyan",
    ))


@cli.command()
@click.option("--platform", "--pl", default="freepik", help="Target platform (pixta, adobe-stock, freepik)")
@click.option("--email", default=None, help="Platform login email")
@click.option("--password", default=None, help="Platform login password")
@click.option("--headless", is_flag=True, help="Run CloakBrowser headless")
@click.option("--skip-upload", is_flag=True, help="Skip file upload, only login")
def upload(
    platform: str,
    email: Optional[str],
    password: Optional[str],
    headless: bool,
    skip_upload: bool,
):
    """使用 CloakBrowser 上傳 output 目錄下的所有現有 JPEG 圖片。"""
    cfg = get_config()
    output_dir = Path(cfg.output.dir)

    # Find all JPEG files in output
    image_paths = sorted([str(p) for p in output_dir.glob("*.jpg")] + [str(p) for p in output_dir.glob("*.jpeg")])
    if not image_paths:
        console.print("[red]No JPG/JPEG images found in output directory.[/red]")
        sys.exit(1)

    console.print(f"Found {len(image_paths)} images to upload.")

    # Resolve credentials
    if platform == "pixta":
        cred_email = email or cfg.pixta.contributor.email
        cred_password = password or cfg.pixta.contributor.password
    elif platform == "adobe-stock":
        cred_email = email or cfg.adobe.contributor.email
        cred_password = password or cfg.adobe.contributor.password
    elif platform == "freepik":
        cred_email = email or (cfg.freepik.contributor.email if hasattr(cfg.freepik, 'contributor') else "")
        cred_password = password or (cfg.freepik.contributor.password if hasattr(cfg.freepik, 'contributor') else "")
    else:
        cred_email = email or ""
        cred_password = password or ""

    console.print(f"\n[bold]Launching CloakBrowser for {platform}...[/bold]")

    try:
        with CloakUploader(
            platform=platform,
            headless=headless,
            slow_mo=500,
            humanize=True,
        ) as uploader:
            uploader.run(
                metadata_list=[],
                file_paths=image_paths if not skip_upload else None,
                email=cred_email,
                password=cred_password,
                skip_upload=skip_upload,
                skip_metadata=True,
            )
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user.[/yellow]")
    except Exception as e:
        console.print(f"[red]CloakBrowser error: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())


if __name__ == "__main__":
    cli()
