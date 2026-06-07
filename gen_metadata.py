#!/usr/bin/env python3
"""Upscale 53 images to 6MP and generate metadata CSV."""
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from src.metadata import write_metadata_csv, write_freepik_csv, ImageMetadata
from src.config import load_config, get_config

ROOT = Path(__file__).parent
OUTPUT = ROOT / "output"
load_config(str(ROOT / "config.yaml"))

# 1. Load prompts from file
prompts = []
with open(ROOT / "prompts_50.txt") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            prompts.append(line)

# 2. Get all new images (sorted by timestamp)
images = sorted(OUTPUT.glob("stock_*.jpg"))
print(f"Images found: {len(images)}")

# 3. Category mapping based on prompt content
CATEGORY_RULES = [
    ("business", "business-finance"),
    ("office", "business-finance"),
    ("corporate", "business-finance"),
    ("professional", "business-finance"),
    ("technology", "technology"),
    ("digital", "technology"),
    ("cyber", "technology"),
    ("robot", "technology"),
    ("circuit", "technology"),
    ("data", "technology"),
    ("mountain", "nature"),
    ("lake", "nature"),
    ("forest", "nature"),
    ("landscape", "nature"),
    ("sunset", "nature"),
    ("waterfall", "nature"),
    ("ocean", "nature"),
    ("sea", "nature"),
    ("wave", "nature"),
    ("flower", "nature"),
    ("lavender", "nature"),
    ("sunrise", "nature"),
    ("food", "food-drink"),
    ("breakfast", "food-drink"),
    ("bowl", "food-drink"),
    ("chef", "food-drink"),
    ("herbs", "food-drink"),
    ("bakery", "food-drink"),
    ("smoothie", "food-drink"),
    ("yoga", "sports-fitness"),
    ("fitness", "sports-fitness"),
    ("athlete", "sports-fitness"),
    ("beach", "travel"),
    ("travel", "travel"),
    ("vacation", "travel"),
    ("tropical", "travel"),
    ("destination", "travel"),
    ("cappadocia", "travel"),
    ("medical", "healthcare-medical"),
    ("hospital", "healthcare-medical"),
    ("dental", "healthcare-medical"),
    ("laboratory", "healthcare-medical"),
    ("science", "science"),
    ("abstract", "abstract"),
    ("geometric", "abstract"),
    ("art", "abstract"),
    ("marble", "abstract"),
    ("education", "education"),
    ("learning", "education"),
    ("student", "education"),
    ("study", "education"),
    ("school", "education"),
    ("classroom", "education"),
    ("architecture", "buildings-landmarks"),
    ("city", "buildings-landmarks"),
    ("skyline", "buildings-landmarks"),
    ("building", "buildings-landmarks"),
    ("warehouse", "industrial"),
    ("factory", "industrial"),
    ("construction", "industrial"),
    ("wedding", "holidays"),
    ("christmas", "holidays"),
    ("interior", "buildings-landmarks"),
    ("living", "buildings-landmarks"),
    ("bedroom", "buildings-landmarks"),
    ("bathroom", "buildings-landmarks"),
    ("kitchen", "food-drink"),
    ("showroom", "buildings-landmarks"),
    ("apartment", "buildings-landmarks"),
    ("automotive", "technology"),
    ("car", "technology"),
    ("transportation", "technology"),
    ("furniture", "buildings-landmarks"),
    ("home", "buildings-landmarks"),
    ("music", "illustrations-vectors"),
    ("vinyl", "illustrations-vectors"),
    ("retro", "vintage"),
    ("vintage", "vintage"),
    ("garden", "nature"),
    ("plant", "nature"),
    ("tree", "nature"),
    ("space", "science"),
    ("nebula", "science"),
    ("galaxy", "science"),
    ("astronomical", "science"),
    ("cloud", "nature"),
    ("sky", "nature"),
]

def classify_category(prompt: str) -> str:
    pl = prompt.lower()
    for keyword, cat in CATEGORY_RULES:
        if keyword in pl:
            return cat
    return "illustrations-vectors"

extras_map = {
    "business-finance": ["Business", "Corporate", "Office", "Professional", "Teamwork", "Career", "Success", "Meeting", "Collaboration"],
    "technology": ["Technology", "Digital", "Innovation", "Data", "Futuristic", "Cyber", "Network", "Circuit", "Robot", "AI"],
    "nature": ["Nature", "Landscape", "Scenic", "Outdoor", "Environment", "Forest", "Mountain", "Lake", "Sunset", "Wilderness"],
    "food-drink": ["Food", "Healthy", "Nutrition", "Cuisine", "Fresh", "Cooking", "Breakfast", "Fruit", "Gourmet", "Recipe"],
    "sports-fitness": ["Fitness", "Wellness", "Health", "Lifestyle", "Exercise", "Yoga", "Meditation", "Active", "Workout", "Motion"],
    "travel": ["Travel", "Vacation", "Holiday", "Adventure", "Destination", "Explore", "Wanderlust", "Journey", "Tourism", "Trip"],
    "healthcare-medical": ["Healthcare", "Medical", "Hospital", "Health", "Medicine", "Clinical", "Treatment", "Care", "Doctor", "Patient"],
    "abstract": ["Abstract", "Art", "Design", "Modern", "Graphic", "Pattern", "Creative", "Colorful", "Contemporary", "Texture"],
    "education": ["Education", "Learning", "Study", "School", "Books", "Knowledge", "Student", "Academic", "Reading", "Classroom"],
    "buildings-landmarks": ["Architecture", "City", "Urban", "Modern", "Building", "Interior", "Design", "Structure", "Real Estate", "Property"],
    "science": ["Science", "Research", "Space", "Laboratory", "Astronomy", "Cosmic", "Universe", "Discovery", "Innovation", "Technology"],
    "industrial": ["Industrial", "Factory", "Manufacturing", "Engineering", "Construction", "Warehouse", "Logistics", "Worker", "Safety", "Heavy"],
    "holidays": ["Holiday", "Celebration", "Wedding", "Event", "Festive", "Party", "Romantic", "Ceremony", "Love", "Decoration"],
    "vintage": ["Vintage", "Retro", "Classic", "Nostalgic", "Antique", "Old", "Vinyl", "Music", "Record", "Analog"],
    "illustrations-vectors": ["Illustration", "Vector", "Art", "Graphic", "Decorative", "Design", "Clip Art", "Icon", "Drawing", "Visual"],
}

metadata_list = []
stopwords = {"a", "an", "the", "in", "on", "at", "of", "for", "with", "and", "or", "by", "to", "from", "is", "are", "it", "its", "this", "that"}

for i, img_path in enumerate(images):
    # Determine prompt index (take modulo since prompts might be fewer)
    prompt = prompts[i % len(prompts)] if i < len(prompts) else f"Stock photo number {i+1}"
    cat = classify_category(prompt)

    # Upscale to 6MP using common helper
    from src.image_utils import upscale_image_to_mp
    upscale_image_to_mp(img_path, target_mp=6.0, quality=95)
    
    # Reload to get actual size
    img = Image.open(img_path)
    target_w, target_h = img.size
    mp = target_w * target_h / 1000000

    # Generate keywords from prompt
    words = prompt.lower().split()
    keywords = []
    seen = set()
    for w in words:
        w = w.strip(".,;:!?'\"")
        if w not in stopwords and len(w) > 2 and w not in seen:
            seen.add(w)
            keywords.append(w.title())

    extras = extras_map.get(cat, ["Stock", "Photo", "Image"])
    for e in extras:
        if e.lower() not in seen:
            seen.add(e.lower())
            keywords.append(e)

    title = prompt.strip().rstrip(".,")
    if not title.endswith("."):
        title += "."
    title = title[0].upper() + title[1:] if not title[0].isupper() else title

    meta = ImageMetadata(
        filename=img_path.name,
        title=title[:200],
        description=title,
        keywords=keywords[:30],
        category=cat,
        ai_generated=True,
        has_releases=False,
        prompt=prompt,
        model=get_config().freepik.metadata.model,
    )
    metadata_list.append(meta)

    if (i+1) % 10 == 0 or i == 0:
        print(f"  [{i+1}/{len(images)}] {img_path.name[:20]:20s} -> {target_w}x{target_h} ({mp:.0f}MP) {cat}")

# Write CSV
csv_path = OUTPUT / "metadata.csv"
write_metadata_csv(metadata_list, str(csv_path))
write_freepik_csv(metadata_list, str(OUTPUT / "metadata_freepik.csv"))
print(f"\nComplete: {len(metadata_list)} images")
print(f"CSV (Adobe): {csv_path}")
print(f"CSV (Freepik): {OUTPUT / 'metadata_freepik.csv'}")
