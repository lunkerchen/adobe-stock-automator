"""
Browser 自動化 — 登入 Adobe Stock Contributor，上傳檔案，提交 metadata

流程:
1. 登入 contributor.stock.adobe.com（或要求使用者手動登入 + 驗證 email）
2. 上傳圖片（透過網頁的 drag-and-drop 或 file input）
3. 等待上傳完成
4. 逐個填寫 metadata（title, keywords, category, AI tag）
5. 提示使用者手動提交
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from rich.console import Console

from .config import get_config
from .metadata import ImageMetadata

console = Console()


class AdobeStockBrowserSubmitter:
    """
    Playwright-based browser automation for Adobe Stock contributor.
    Handles: login → file upload → metadata fill.
    """

    def __init__(self):
        cfg = get_config().browser
        self.headless = cfg.headless
        self.slow_mo = cfg.slow_mo
        self.submit_url = cfg.submit_url
        self.cookie_cache = Path(cfg.cookie_cache)
        self._pw = None
        self._browser = None
        self._context = None
        self._page = None

    async def __aenter__(self):
        from playwright.async_api import async_playwright

        self._pw = await async_playwright().start()
        self._browser = await self._pw.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo,
        )

        self._context = await self._browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )

        if self.cookie_cache.exists():
            cookies = json.loads(self.cookie_cache.read_text())
            await self._context.add_cookies(cookies)
            console.print("[dim]Loaded cached cookies[/dim]")

        self._page = await self._context.new_page()
        return self

    async def __aexit__(self, *args):
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._pw:
            await self._pw.stop()

    # ── Login ──────────────────────────────────────────────

    async def login(self) -> bool:
        """Navigate to contributor page. Login if needed (or ask user to)."""
        page = self._page
        cfg = get_config().adobe.contributor

        console.print(f"\n[bold]Opening {self.submit_url}...[/bold]")
        await page.goto(self.submit_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

        current_url = page.url

        # Already logged in?
        if "uploads" in current_url or "dashboard" in current_url:
            console.print("[green]✓[/green] Already logged in (cached cookie)")
            return True

        # On login page?
        if "auth.services.adobe.com" in current_url:
            console.print("[yellow]Adobe login required.[/yellow]")

            # Type email
            email_input = page.locator("input[type='email']").first
            if await email_input.is_visible():
                await email_input.fill(cfg.email)
                await page.locator("button[type='submit']").first.click()
                await page.wait_for_timeout(2000)

            # Check for security challenge
            if "passkey" in page.url.lower() or "passkey" in (await page.content()).lower():
                console.print(
                    "[yellow]⚠ Adobe requires email verification or passkey.[/yellow]\n"
                    "  The browser window is open. Please:\n"
                    "  1. Click 'Email code to l***@d***.com'\n"
                    "  2. Check your email for the verification code\n"
                    "  3. Enter it in the browser\n"
                    "  4. You have 5 minutes\n"
                )
                # Save cookies and wait for user to complete login
                await self._save_cookies()

                # Poll until login completes
                for _ in range(60):  # 5 min timeout
                    await page.wait_for_timeout(5000)
                    if "uploads" in page.url or "dashboard" in page.url:
                        console.print("[green]✓[/green] Login successful!")
                        await self._save_cookies()
                        return True
                console.print("[red]Login timeout. Run again with --submit once logged in.[/red]")
                return False

        return False

    async def _save_cookies(self):
        self.cookie_cache.parent.mkdir(parents=True, exist_ok=True)
        cookies = await self._context.cookies()
        self.cookie_cache.write_text(json.dumps(cookies, indent=2))

    # ── File Upload ────────────────────────────────────────

    async def upload_files(self, file_paths: list[str]) -> bool:
        """Upload files via the web upload interface."""
        page = self._page

        # Look for file input or drop zone
        file_input = page.locator("input[type='file']").first
        drop_zone = page.locator("div[data-test-id='upload-dropzone']").first

        if await file_input.is_visible():
            console.print(f"  Uploading {len(file_paths)} files via file input...")
            await file_input.set_input_files(file_paths)
            await page.wait_for_timeout(3000)
            return True
        elif await drop_zone.is_visible():
            console.print(f"  Uploading {len(file_paths)} files via drop zone...")
            # Use file input inside the drop zone
            inner_input = drop_zone.locator("input[type='file']").first
            if await inner_input.is_visible():
                await inner_input.set_input_files(file_paths)
                await page.wait_for_timeout(3000)
                return True
            else:
                console.print("[yellow]  Drop zone found but file input not accessible.[/yellow]")
                console.print("  Drag files manually into the browser window.")
                return False
        else:
            console.print("[yellow]  No upload area found — files may already be uploaded.[/yellow]")
            # May be on the submit page with existing files
            return True

    async def wait_for_upload_complete(self, timeout_sec: int = 120):
        """Wait for upload processing to finish."""
        console.print("  Waiting for upload to complete...", end="")
        for _ in range(timeout_sec):
            # Check if spinner is gone
            spinner = self._page.locator(
                "div[class*='spinner'], div[class*='progress'], div[aria-busy='true']"
            ).first
            if not await spinner.is_visible():
                console.print(" [green]done[/green]")
                return True
            await self._page.wait_for_timeout(1000)
            console.print(".", end="")
        console.print(" [yellow]timeout[/yellow]")
        return False

    # ── Metadata Fill ─────────────────────────────────────

    async def fill_metadata(self, meta: ImageMetadata) -> bool:
        """Fill metadata for the currently selected asset."""
        page = self._page

        try:
            # ── Title ──
            title_input = None
            for sel in [
                "input[data-test-id='title-input']",
                "input[placeholder*='Title' i]",
                "input[name='title']",
                "input[id*='title']",
                "input[aria-label*='title' i]",
                "textarea[placeholder*='title' i]",
                "textarea[aria-label*='title' i]",
                "textarea[data-test-id='title-input']",
                "input:not([type='hidden']):not([type='file'])",
            ]:
                el = page.locator(sel).first
                if await el.is_visible():
                    title_input = el
                    break

            if title_input:
                await title_input.click()
                await title_input.fill("")
                await title_input.fill(meta.title[:200])
                console.print(f"  ✓ Title: {meta.title[:60]}...")
            else:
                console.print("  [yellow]⚠ Title not found[/yellow]")

            # ── Keywords ──
            kw_input = None
            for sel in [
                "textarea[data-test-id='keywords-input']",
                "textarea[placeholder*='keyword' i]",
                "input[placeholder*='keyword' i]",
                "textarea[name='keywords']",
                "textarea[id*='keyword']",
                "textarea[aria-label*='keyword' i]",
                "div[class*='keywords'] textarea",
                "div[class*='keyword'] input",
            ]:
                el = page.locator(sel).first
                if await el.is_visible():
                    kw_input = el
                    break

            if kw_input:
                kw_text = ", ".join(meta.keywords)
                await kw_input.click()
                await kw_input.fill("")
                await kw_input.fill(kw_text)
                console.print(f"  ✓ Keywords: {len(meta.keywords)}")
            else:
                console.print("  [yellow]⚠ Keywords not found[/yellow]")

            # ── Generative AI checkbox ──
            if meta.ai_generated:
                for sel in [
                    "input[data-test-id='generative-ai-checkbox']",
                    "label:has-text('Generative AI') input[type='checkbox']",
                    "label:has-text('Created using generative') input[type='checkbox']",
                    "label:has-text('AI') input[type='checkbox']",
                    "label:has-text('Generated by AI') input[type='checkbox']",
                    "input[aria-label*='generative ai' i]",
                    "input[aria-label*='AI' i]",
                    "span:has-text('Generative AI') input[type='checkbox']",
                ]:
                    el = page.locator(sel).first
                    if await el.is_visible():
                        is_checked = await el.is_checked()
                        if not is_checked:
                            await el.click()
                            console.print("  ✓ Generative AI: checked")
                        break

            console.print(f"[green]✓[/green] {meta.filename} filled")
            return True

        except Exception as e:
            console.print(f"[red]✗[/red] {meta.filename}: {e}")
            return False

    # ── Full Pipeline ──────────────────────────────────────

    async def run(
        self,
        metadata_list: list[ImageMetadata],
        file_paths: list[str] | None = None,
    ) -> int:
        """
        Full workflow:
          1. Login (or wait for manual login)
          2. Upload files
          3. Fill metadata
          4. Instructions to submit
        """
        if not await self.login():
            return 0

        # Upload files if provided and upload area visible
        if file_paths:
            console.print(f"\n[bold]Uploading {len(file_paths)} files...[/bold]")
            if await self.upload_files(file_paths):
                await self.wait_for_upload_complete()
            else:
                console.print("[yellow]Manual upload required. Drag files into the browser.[/yellow]")

        # Fill metadata
        console.print(f"\n[bold]Filling metadata for {len(metadata_list)} assets...[/bold]")
        success = 0
        for idx, meta in enumerate(metadata_list):
            console.print(f"\n[{idx + 1}/{len(metadata_list)}] {meta.filename}")

            # Click on the tile if needed
            tile = self._page.locator(f"text={meta.filename}").first
            if await tile.is_visible():
                await tile.click()
                await self._page.wait_for_timeout(1000)

            if await self.fill_metadata(meta):
                success += 1

        console.print(f"\n[bold green]✓ {success}/{len(metadata_list)} assets processed[/bold green]")
        console.print(
            "\n[yellow]⚠ Files are tagged but NOT yet submitted.[/yellow]\n"
            "  Go to the browser window, review, and click 'Submit All'."
        )
        return success
