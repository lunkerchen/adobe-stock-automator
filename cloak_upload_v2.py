#!/usr/bin/env python3
"""Upload 3 JPGs to Adobe Stock via CloakBrowser with cached cookies."""
from cloakbrowser import launch
import time, os, json

BASE = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(BASE, "output")
COOKIE_FILE = os.path.join(BASE, ".cookies", "adobe_stock_cloak.json")
URL = "https://contributor.stock.adobe.com/en/uploads"

FILES = [
    os.path.join(OUTPUT, "stock_team_collab.jpg"),
    os.path.join(OUTPUT, "stock_digital_tech.jpg"),
    os.path.join(OUTPUT, "stock_mountain_lake.jpg"),
]

print("Starting CloakBrowser...")
browser = launch(headless=False)

# Create context and load cookies
ctx = browser.new_context(viewport={"width": 1440, "height": 900})
if os.path.exists(COOKIE_FILE):
    cookies = json.loads(open(COOKIE_FILE).read())
    ctx.add_cookies(cookies)
    print(f"✓ Loaded {len(cookies)} cookies")

page = ctx.new_page()
page.goto(URL, wait_until="domcontentloaded", timeout=60000)
time.sleep(3)

print(f"URL: {page.url}")
print(f"Title: {page.title()}")

if "uploads" in page.url.lower():
    print("✓ Logged in!")
else:
    print("→ Login needed. Log in now in the browser...")
    for _ in range(120):
        time.sleep(5)
        if "uploads" in page.url.lower():
            print("✓ Logged in!")
            # Save cookies for next time
            cookies = ctx.cookies()
            with open(COOKIE_FILE, "w") as f:
                json.dump(cookies, f)
            print("  Cookies saved")
            break

# Upload
print("\n=== Upload ===")
valid = [f for f in FILES if os.path.exists(f)]
print(f"Files: {len(valid)}")

# Show page structure
info = page.evaluate("""() => {
    const r = [];
    const btns = document.querySelectorAll('button');
    r.push('Buttons:');
    for (const b of btns) {
        if (b.offsetParent !== null) r.push('  ' + (b.textContent||'').trim().slice(0,60));
    }
    const fis = document.querySelectorAll('input[type="file"]');
    r.push('File inputs: ' + fis.length);
    return r.join('\\n');
}""")
print(info)

# Try file upload
for attempt in range(5):
    page.evaluate("""() => {
        for (const b of document.querySelectorAll('button')) {
            const t = (b.textContent||'').toLowerCase();
            if ((t.includes('upload')||t.includes('add')||t.includes('new')||t.includes('browse')||t.includes('select')) && b.offsetParent !== null) {
                b.click(); return 'clicked: ' + t;
            }
        }
        return null;
    }""")
    time.sleep(2)
    try:
        fi = page.locator("input[type='file']").first
        fi.set_input_files(valid)
        print("✓ Files uploaded!")
        time.sleep(5)
        break
    except:
        continue
else:
    print("⚠ Auto-upload failed. Drag files from Finder:")

for f in valid:
    print(f"  {f}")

print("\nmetadata.csv ready:", os.path.join(OUTPUT, "metadata.csv"))
print("Browser open. Upload files, fill metadata, Submit All.")
print("Tell me when done.")

while True:
    time.sleep(30)
