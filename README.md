# Adobe Stock Automator

AI 圖庫圖片自動化生成 + 上架工具。支援 Codex CLI（ChatGPT 訂閱）或 OpenAI/Stability/Replicate 等多種生圖引擎，自動產出 Adobe Stock 規格的圖片與 Metadata，並透過 Playwright 瀏覽器自動化上傳。

## 流程

```
提示詞 → AI 生圖 → 6MP Upscale → Metadata CSV → 瀏覽器開啟 → 自動填寫 → 你按 Submit All
```

不用 FTP，不用 API key（可選），直接用 ChatGPT 訂閱或免費 dummy provider。

## Adobe Stock 政策

✅ **接受 AI 生成內容** — 只需在提交時勾選 Generative AI 標籤（本工具自動處理）。

## 快速開始

```bash
# 安裝相依套件
pip install -r requirements.txt

# 設定
cp config.example.yaml config.yaml
# 填入 adobe.contributor 的 email 和 password

# 免 API key 測試（dummy provider）
python3 main.py generate "test image" -n 2 -p dummy

# 完整流程（用 ChatGPT 訂閱生圖 → 瀏覽器上傳）
python3 main.py generate "business team meeting modern office" -n 3

# 批次處理（從檔案讀多個 prompt）
python3 main.py batch prompts/example.txt -n 1 -p dummy
```

## CLI 指令

| 指令 | 用途 |
|------|------|
| `generate` | 生圖 → Metadata → 瀏覽器上傳（一鍵流程） |
| `cloak` | 使用 CloakBrowser（stealth Chromium）上傳 |
| `portal_upload` | Adobe Stock Portal 專用上傳模組 |
| `batch` | 批次處理（一行一 prompt） |
| `requirements` | 顯示各平台圖庫規格 |

### 批次生圖（50 張）

```bash
bash run_50.sh
```

使用 `dashboard/scripts/codex-gen-wrapper.sh` 跑 Codex CLI 平行生圖，批次 10 張，約 3-5 分鐘完成 50 張。

## 專案結構

```
adobe-stock-automator/
├── main.py                     # CLI 入口 (click)
├── src/
│   ├── config.py               # YAML 設定載入
│   ├── generate.py             # 圖片生成 (dummy/openai/stability/replicate/local)
│   ├── metadata.py             # Metadata 生成 + CSV 輸出
│   ├── upload.py               # FTP 上傳 (stub)
│   ├── submit_browser.py       # Playwright 瀏覽器自動化
│   ├── portal_upload.py        # Adobe Portal 專用上傳
│   └── upload_cloak.py         # CloakBrowser Stealth 上傳
├── dashboard/                  # Next.js 網頁版 Dashboard
│   ├── src/app/                # App Router: Generate / Gallery / Config
│   ├── scripts/codex-gen-wrapper.sh  # Codex CLI 生圖 wrapper
│   └── ... (Next.js + shadcn/ui + zh-TW/en i18n)
├── config.example.yaml
├── prompts/example.txt
├── prompts_50.txt              # 50 個商用 prompt 範本
├── gen_metadata.py             # Metadata 批次產生 + 6MP upscale
├── run_50.sh                   # 50 張批次生圖腳本
└── README.md
```

## Upload 方式

| 方法 | 狀態 | 說明 |
|------|------|------|
| Web Browser | ✅ 推薦 | Playwright 自動化，支援 email 驗證等待 |
| CloakBrowser | ✅ 可用 | Stealth Chromium，支援 cookie 持久化 |
| Portal Upload | ✅ 可用 | Adobe Stock Portal 專用模組 |
| FTP | ⛔ 已不活躍 | Adobe 似乎已棄用 FTP |
| API | ❌ 無 | Adobe 無公開 contributor API |

## 生圖 Provider

| Provider | 需要 | 說明 |
|----------|------|------|
| `dummy` | 無 | 生成漸層色測試圖，免 API key |
| `openai` | OPENAI_API_KEY | DALL-E 3 |
| `stability` | STABILITY_API_KEY | Stable Diffusion 3.5 |
| `replicate` | REPLICATE_API_TOKEN | 多種模型 |
| `local` | torch + diffusers | 本機 GPU 推論 |
| Codex CLI | ChatGPT 訂閱 | 透過 `codex-gen-wrapper.sh` 使用 |

## 隱私安全

- `config.yaml` 含有你的 Adobe 帳密 → 已加入 `.gitignore`
- Cookie 快取在 `.cookies/` → 已加入 `.gitignore`
- 產出圖片在 `output/` → 已加入 `.gitignore`

## 授權

MIT — Laban Chen
