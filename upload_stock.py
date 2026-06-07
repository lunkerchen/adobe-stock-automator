#!/usr/bin/env python3
"""
Adobe Stock uploader — opens browser, helps you upload + tag 3 images.
"""
import json, sys, yaml, asyncio
from pathlib import Path

ROOT = Path(__file__).parent
OUTPUT = ROOT / "output"
cfg = yaml.safe_load((ROOT / "config.yaml").read_text())

IMAGES = [
    {
        "file": "stock_team_collab.png",
        "title": "Modern diverse business team collaborating in bright minimalist office",
        "kw": "business, team, collaboration, office, diverse, professional, meeting, laptop, modern, workplace",
    },
    {
        "file": "stock_digital_tech.png",
        "title": "Digital transformation concept with glowing circuit patterns and holographic interface",
        "kw": "technology, digital, futuristic, circuit, hologram, data, innovation, AI, cyber, network",
    },
    {
        "file": "stock_mountain_lake.png",
        "title": "Serene mountain lake landscape at golden hour with misty pine forest reflection",
        "kw": "nature, landscape, mountain, lake, sunset, forest, golden hour, scenic, travel, peaceful",
    },
]

async def main():
    from playwright.async_api import async_playwright

    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=False, slow_mo=500)
    ctx = await browser.new_context(viewport={"width": 1440, "height": 900})
    page = await ctx.new_page()

    url = "https://contributor.stock.adobe.com/en/uploads"
    print(f"1. Opening {url} ...")
    await page.goto(url, wait_until="domcontentloaded")
    await page.wait_for_timeout(5000)
    print(f"   Current URL: {page.url}")
    print(f"   Title: {await page.title()}")

    # Check login
    if "uploads" in page.url or "dashboard" in page.url:
        print("   ✓ Already logged in")
    else:
        print("   → Need to login. Check the browser window.")
        email = page.locator("input[type='email']").first
        if await email.is_visible():
            await email.fill(cfg["adobe"]["contributor"]["email"])
            await page.locator("button[type='submit']").first.click()
            await page.wait_for_timeout(3000)

        pw_el = page.locator("input[type='password']").first
        if await pw_el.is_visible():
            await pw_el.fill(cfg["adobe"]["contributor"]["password"])
            await page.locator("button[type='submit']").first.click()
            await page.wait_for_timeout(3000)

        if "passkey" in page.url.lower():
            print("   ⚠ Passkey/email verification needed. Do it in the browser.")
            for _ in range(60):
                await page.wait_for_timeout(5000)
                if "uploads" in page.url: break

    # Take a screenshot so we can see what's on the page
    await page.screenshot(path="/tmp/adobe-upload-page.png")
    print("2. Screenshot saved to /tmp/adobe-upload-page.png")

    # Try to find and click the upload button
    for btn_text in ["Upload", "upload", "Add files", "New submission"]:
        btn = page.locator(f"button:has-text('{btn_text}')").first
        if await btn.is_visible():
            print(f"   ✓ Found '{btn_text}' button, clicking...")
            await btn.click()
            await page.wait_for_timeout(2000)
            break

    # Try file upload
    file_paths = [str(OUTPUT / img["file"]) for img in IMAGES]
    for fp in file_paths:
        if not Path(fp).exists():
            print(f"   ✗ Missing: {fp}")
            continue

    file_input = page.locator("input[type='file']").first
    if await file_input.is_visible():
        await file_input.set_input_files([p for p in file_paths if Path(p).exists()])
        print("   ✓ Files selected for upload")
        await page.wait_for_timeout(8000)
    else:
        print("   ⚠ File input not found. Drag & drop files into the browser window.")
        print("   The browser is open — drag the images from Finder into the upload area.")

    # Let user do the rest manually
    print(f"\n{'='*60}")
    print("""NEXT STEPS:
1. Drop the 3 image files into the browser upload area (if not already uploaded)
2. Wait for upload to finish
3. Fill in Title field with something descriptive
4. Add Keywords (comma-separated)
5. Check 'Generative AI' checkbox
6. Click 'Submit All'
""")
    print("Image files:")
    for img in IMAGES:
        fp = OUTPUT / img["file"]
        sz = fp.stat().st_size / 1024 / 1024
        print(f"   📄 {img['file']}  ({sz:.1f}MB)")
        print(f"      Title: {img['title']}")
        print(f"      Keywords: {img['kw']}")
    print(f"{'='*60}")

    # Keep browser open
    await page.pause()  # keeps browser open in Playwright inspector mode

if __name__ == "__main__":
    asyncio.run(main())
