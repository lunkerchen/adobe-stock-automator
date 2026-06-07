#!/usr/bin/env python3
"""Open Playwright Chromium at Adobe login."""
from playwright.sync_api import sync_playwright
import time

LOGIN_URL = "https://auth.services.adobe.com/en_US/index.html"

print("Starting browser...")
with sync_playwright() as pw:
    browser = pw.chromium.launch(
        headless=False,
        args=["--no-sandbox"],
    )
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    # Test network
    print("Testing network...")
    page.goto("https://example.com", wait_until="domcontentloaded", timeout=15000)
    print("✓ Network OK")

    print("Navigating to Adobe login...")
    page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)
    print(f"✓ Page: {page.title()}")
    print("  Enter credentials in browser.")
    print("  Tell me when done.\n")
    while True:
        time.sleep(30)
