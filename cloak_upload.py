#!/usr/bin/env python3
"""Upload 3 images (resized to 4MP+) to Adobe Stock."""
import sys, os, time
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from src.config import load_config, get_config
from src.metadata import ImageMetadata
from src.upload_cloak import CloakUploader, CONFIRM_NODE_SUBMIT

load_config(os.path.join(BASE, "config.yaml"))
cfg = get_config()
OUTPUT_DIR = os.path.join(BASE, cfg.output.dir.lstrip("./"))

IMAGES = [
    {
        "file": "stock_team_collab.jpg",
        "title": "Modern diverse business team collaborating in bright minimalist office with plants",
        "desc": "Professional multi-ethnic team working together around a laptop in a modern office space",
        "kw": ["business", "team", "collaboration", "office", "diverse", "professional", "meeting", "laptop", "modern", "workplace"],
        "cat": "Business/Finance",
    },
    {
        "file": "stock_digital_tech.jpg",
        "title": "Digital transformation concept with glowing circuit patterns and holographic interface",
        "desc": "Futuristic technology concept with hand interacting with holographic digital interface",
        "kw": ["technology", "digital", "futuristic", "circuit", "hologram", "data", "innovation", "AI", "cyber", "network"],
        "cat": "Technology",
    },
    {
        "file": "stock_mountain_lake.jpg",
        "title": "Serene mountain lake landscape at golden hour with misty pine forest reflection",
        "desc": "Beautiful nature landscape of a calm mountain lake surrounded by pine forest at sunset",
        "kw": ["nature", "landscape", "mountain", "lake", "sunset", "forest", "golden hour", "scenic", "travel", "peaceful"],
        "cat": "Nature",
    },
]

# Auto-confirm nodes
import src.upload_cloak as uc
_original_confirm = uc.CloakUploader.confirm_node
def _skip_confirm(self, node_type, message, timeout_minutes=5):
    return True
uc.CloakUploader.confirm_node = _skip_confirm

metadata_list = []
file_paths = []

for img in IMAGES:
    fp = os.path.join(OUTPUT_DIR, img["file"])
    if not os.path.exists(fp):
        print(f"✗ Missing: {fp}")
        continue
    file_paths.append(os.path.abspath(fp))
    meta = ImageMetadata(
        filename=img["file"],
        title=img["title"],
        description=img["desc"],
        keywords=img["kw"],
        category=img["cat"],
        ai_generated=True,
        has_releases=False,
    )
    metadata_list.append(meta)
    sz = os.path.getsize(fp) / 1024 / 1024
    print(f"  ✓ {img['file']} ({sz:.1f}MB)")

if not file_paths:
    print("No files!")
    sys.exit(1)

print(f"\nLaunching CloakBrowser...")
with CloakUploader(platform="adobe-stock", headless=False, slow_mo=800, humanize=True) as uploader:
    uploader.run(
        metadata_list=metadata_list,
        file_paths=file_paths,
        email=cfg.adobe.contributor.email,
        password=cfg.adobe.contributor.password,
        skip_upload=False,
        skip_metadata=False,
    )

print("\n✓ Done. Browser stays open — review and Submit All.")
while True:
    time.sleep(30)
