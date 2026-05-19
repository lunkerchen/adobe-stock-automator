#!/usr/bin/env python3
"""Open CloakBrowser at Adobe Stock upload page — manual upload."""
from cloakbrowser import launch
import time

print("Starting CloakBrowser...")
browser = launch(headless=False)
page = browser.new_page(viewport={"width": 1440, "height": 900})

url = "https://contributor.stock.adobe.com/en/uploads"
page.goto(url, wait_until="domcontentloaded", timeout=30000)
page.wait_for_timeout(5000)

print(f"Page: {page.title()}")
if "login" in page.url.lower() or "auth" in page.url.lower():
    print("→ Login page. Log in with Adobe credentials.")
    for _ in range(120):
        time.sleep(5)
        if "uploads" in page.url.lower():
            print("✓ Logged in!")
            break

print("\n✓ Browser ready.")
print("Files to upload (drag into browser window):")
for f in ["stock_team_collab.jpg", "stock_digital_tech.jpg", "stock_mountain_lake.jpg"]:
    fp = f"/Users/lunker/Projects/adobe-stock-automator/output/{f}"
    print(f"  {fp}")
print("\nAfter upload, fill Title + Keywords + Generative AI + Submit All.")
print("Tell me when done.")
while True:
    time.sleep(30)
