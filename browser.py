#!/usr/bin/env python3
"""Open CloakBrowser at Adobe Stock upload page — keep cookies intact."""
from cloakbrowser import launch
import time

print("Starting CloakBrowser — cookies preserved...")
browser = launch(headless=False)
page = browser.new_page(viewport={"width": 1440, "height": 900})

url = "https://contributor.stock.adobe.com/en/uploads"
page.goto(url, wait_until="domcontentloaded", timeout=30000)
page.wait_for_timeout(3000)

print(f"Page: {page.title()}")
if "login" in page.url.lower() or "auth" in page.url.lower():
    print("→ Log in with your Adobe credentials in the browser.")
    print("  Cookies will be saved — you only need to do this once.")
else:
    print("✓ Already logged in via cached cookies.")

print("\nTo upload:")
print("  Drag ~/Projects/adobe-stock-automator/output/stock_*.jpg")
print("  into the browser, then fill metadata + Submit All.")
print("\nMetadata CSV ready: output/metadata.csv")
print("Tell me when done.\n")

while True:
    time.sleep(30)
