#!/usr/bin/env python3
"""Open browser at Adobe Stock uploads page for manual metadata fill + submit."""
from cloakbrowser import launch
import time

URL = "https://contributor.stock.adobe.com/en/uploads"

print("Opening CloakBrowser...")
browser = launch(headless=False)
page = browser.new_page(viewport={"width": 1440, "height": 900})
page.goto(URL, wait_until="domcontentloaded", timeout=30000)
page.wait_for_timeout(5000)
print(f"✓ Page: {page.title()}")
print("")
print("3 files are uploaded. You need to:")
print("  1. Click each image tile to open its metadata panel")
print("  2. Fill Title field")
print("  3. Add Keywords (comma-separated)")
print("  4. Check 'Generative AI' checkbox")
print("  5. Click 'Submit All'")
print("")
print("Metadata reference:")
print("  stock_team_collab.png")
print("    Title: Modern diverse business team collaborating in bright minimalist office with plants")
print("    Keywords: business, team, collaboration, office, diverse, professional, meeting, laptop, modern, workplace")
print("")
print("  stock_digital_tech.png")
print("    Title: Digital transformation concept with glowing circuit patterns and holographic interface")
print("    Keywords: technology, digital, futuristic, circuit, hologram, data, innovation, AI, cyber, network")
print("")
print("  stock_mountain_lake.png")
print("    Title: Serene mountain lake landscape at golden hour with misty pine forest reflection")
print("    Keywords: nature, landscape, mountain, lake, sunset, forest, golden hour, scenic, travel, peaceful")
print("")
print("Tell me when done.\n")
while True:
    time.sleep(30)
