# Adobe Stock & Freepik Automator

AI stock image automated generation, optimization, and multi-platform publishing tool. Supports Codex CLI (ChatGPT subscription) or multiple image generation engines such as OpenAI/Stability/Replicate, automatically producing images and metadata that comply with Adobe Stock and Freepik specifications, and uploading via FTPS or CloakBrowser automated web upload.

## Pipeline

```
Prompt ──> AI Generation ──> 6MP Upscale ──> Metadata CSV (Adobe / Freepik) ──> Web/FTP/FTPS Auto Upload
```

## Features

*   **Multi-Platform CSV Support**:
    *   **Adobe Stock**: Outputs comma-separated CSV, automatically converts category names to Adobe Stock numeric IDs.
    *   **Freepik**: Outputs semicolon (`;`) separated CSV (fields: `File name;Title;Keywords;Prompt;Model`), AI-generated content automatically appends `_ai_generated` at the end of keywords, title length is automatically truncated to 100 characters to prevent errors.
*   **Automatic Resolution Optimization (Upscale)**: Automatically detects image resolution; if below the 6MP limit, uses Lanczos filter for lossless upscaling to 6MP+ (3000x2000), ensuring 100% pass through stock platform review.
*   **Robust Web Auto-Upload (CloakBrowser)**: Uses Stealth Chromium to bypass Cloudflare anti-bot mechanisms, supports manual/cookie login persistence, drag-and-drop image upload, and guides users to one-click import the dedicated `metadata_freepik.csv` for batch application.
*   **Secure FTPS Connection**: Supports FTPS (Explicit TLS) bulk high-speed upload for Freepik accounts level 3 and above.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize config file
cp config.example.yaml config.yaml
# Fill in stock account credentials or API keys in config.yaml

# Test image generation (dummy mode for testing without API key, generates both Adobe and Freepik info)
python3 main.py generate "neon retro synthwave sunset" -n 1 -p dummy --freepik

# Upload all existing JPEG images in the output directory (Freepik web upload example)
python3 main.py upload --platform freepik
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `generate` | AI generation → 6MP Upscale → CSV generation → Web upload (use `--freepik` to also generate Freepik output) |
| `upload` | Upload all existing images in the output directory via CloakBrowser (supports adobe-stock, freepik) |
| `cloak` | Integrated "generate + web auto-upload" workflow via CloakBrowser |
| `portal_upload` | Adobe Stock Portal dedicated upload module |
| `batch` | Batch process prompts files |
| `requirements` | Display stock platform image specifications |

### Batch Generation (50 Images)

```bash
bash run_50.sh
```

Uses `dashboard/scripts/codex-gen-wrapper.sh` to run Codex CLI parallel generation, 10 images per batch, completing 50 images in approximately 3-5 minutes.
After generation, run `./gen_metadata.py` to regenerate and update all CSVs.

## Project Structure

```
adobe-stock-automator/
├── main.py                     # CLI entry point (Click)
├── src/
│   ├── config.py               # YAML config loading with environment variable overrides
│   ├── generate.py             # Image generation (dummy/openai/stability/replicate/local)
│   ├── image_utils.py          # Image resolution detection and 6MP+ Lanczos optimization
│   ├── metadata.py             # Metadata generation and Adobe/Freepik dual CSV format output
│   ├── upload.py               # FTP / FTPS (Explicit TLS) upload logic
│   ├── submit_browser.py       # Playwright browser automation
│   ├── portal_upload.py        # Adobe Portal dedicated upload
│   └── upload_cloak.py         # CloakBrowser Stealth upload (Adobe Stock / Freepik)
├── config.example.yaml
├── prompts_50.txt              # 50 commercial prompt templates
├── gen_metadata.py             # Batch image optimization and metadata regeneration tool
├── run_50.sh                   # 50-image batch generation and optimization script
├── README.md                   # Original (Traditional Chinese)
├── README.en.md                # English
├── README.ja.md                # Japanese
├── README.ko.md                # Korean
├── README.es.md                # Spanish
├── README.fr.md                # French
└── README.zh-TW.md             # Traditional Chinese (same as README.md)
```

## Platform Support

| Platform | Web Automation (CloakBrowser) | FTP / FTPS Upload | Notes |
|----------|-------------------------------|-------------------|-------|
| **Adobe Stock** | ✅ Auto-fill fields and AI tags | ❌ No longer active officially | Recommended to use Web mode or CSV import |
| **Freepik** | ✅ Auto drag-and-drop images + one-click CSV import | ✅ Supports FTPS (Explicit TLS) | Accounts below level 3 use Web mode; level 3 and above can use FTPS |

## Privacy & Security

- `config.yaml` contains your personal credentials → added to `.gitignore`
- Cookie cache in `.cookies/` → added to `.gitignore`
- Generated images in `output/` → added to `.gitignore`

## License

MIT — Laban Chen
