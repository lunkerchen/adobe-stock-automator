#!/usr/bin/env python3
"""Open CloakBrowser at Adobe Stock portfolio page for login."""
from cloakbrowser import launch
import time

TARGET_URL = "https://contributor.stock.adobe.com/en/portfolio"

print("Starting CloakBrowser...")
browser = launch(headless=False)
page = browser.new_page(viewport={"width": 1440, "height": 900})
print(f"Navigating to portfolio...")
page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=30000)
page.wait_for_timeout(5000)
print(f"✓ Page: {page.title()}")
print(f"  URL: {page.url}")
print("  Log in with your Adobe credentials in the browser.")
print("  Tell me when done.\n")
while True:
    time.sleep(30)
