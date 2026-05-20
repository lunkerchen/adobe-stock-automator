# Adobe Stock & Freepik Automator

AI 圖庫圖片自動化生成、優化與多平台發布工具。支援 Codex CLI（ChatGPT 訂閱）或 OpenAI/Stability/Replicate 等多種生圖引擎，自動產出符合 Adobe Stock 及 Freepik 規格的圖片與 Metadata，並透過 FTPS 或 CloakBrowser 自動化網頁上傳。

## 流程

```
提示詞 ──> AI 生圖 ──> 6MP Upscale ──> Metadata CSV (Adobe / Freepik) ──> Web/FTP/FTPS 自動上傳
```

## 功能特色

*   **多平台 CSV 規格支援**：
    *   **Adobe Stock**：輸出逗號分隔 CSV，自動將類別名稱轉為 Adobe Stock 規定的數字 ID。
    *   **Freepik**：輸出分號 (`;`) 分隔 CSV（欄位：`File name;Title;Keywords;Prompt;Model`），AI 生成內容會自動在關鍵字尾端追加 `_ai_generated`，標題長度自動截斷至 100 字元以內以防報錯。
*   **自動解析度優化 (Upscale)**：自動偵測圖片解析度，若低於 6MP 限制，則使用 Lanczos 濾鏡無損放大至 6MP+ (3000x2000)，確保 100% 通過圖庫系統審核。
*   **強健的網頁自動上傳 (CloakBrowser)**：使用 Stealth Chromium 繞過 Cloudflare 防爬蟲機制，支援手動/Cookie 登入持久化、拖曳圖片上傳，並引導使用者一鍵導入專屬的 `metadata_freepik.csv` 完成批量套用。
*   **安全 FTPS 連接**：支援 Freepik 等級 3 以上帳號的 FTPS (Explicit TLS) 批量高速上傳。

## 快速開始

```bash
# 安裝相依套件
pip install -r requirements.txt

# 初始化設定檔
cp config.example.yaml config.yaml
# 於 config.yaml 中填入對應的圖庫帳密或 API credentials

# 測試生成圖片 (免 API Key 測試 dummy 模式，同時生成 Adobe 與 Freepik 資訊)
python3 main.py generate "neon retro synthwave sunset" -n 1 -p dummy --freepik

# 上傳 output 目錄下的所有現有 JPEG 圖片 (以 Freepik 網頁端為例)
python3 main.py upload --platform freepik
```

## CLI 指令

| 指令 | 用途 |
|------|------|
| `generate` | AI 生圖 → 6MP Upscale → CSV 產生 → 網頁上傳（可帶 `--freepik` 同步產生 Freepik 輸出） |
| `upload` | 使用 CloakBrowser 上傳 output 目錄下的所有現有圖片 (支援 pixta, adobe-stock, freepik) |
| `cloak` | 使用 CloakBrowser 整合「生圖 + 網頁自動化上傳」流程 |
| `portal_upload` | Adobe Stock Portal 專用上傳模組 |
| `batch` | 批次處理 prompts 檔案 |
| `requirements` | 顯示各平台圖庫圖片規格 |

### 批次生圖（50 張）

```bash
bash run_50.sh
```

使用 `dashboard/scripts/codex-gen-wrapper.sh` 跑 Codex CLI 平行生圖，批次 10 張，約 3-5 分鐘完成 50 張。
生成後可執行 `./gen_metadata.py` 重新更新與生成所有 CSV。

## 專案結構

```
adobe-stock-automator/
├── main.py                     # CLI 入口 (Click)
├── src/
│   ├── config.py               # YAML 設定載入與環境變數覆蓋
│   ├── generate.py             # 圖片生成 (dummy/openai/stability/replicate/local)
│   ├── image_utils.py          # 圖片解析度偵測與 6MP+ Lanczos 優化
│   ├── metadata.py             # Metadata 產生與 Adobe/Freepik 雙 CSV 格式寫入
│   ├── upload.py               # FTP / FTPS (Explicit TLS) 上傳邏輯
│   ├── submit_browser.py       # Playwright 瀏覽器自動化
│   ├── portal_upload.py        # Adobe Portal 專用上傳
│   └── upload_cloak.py         # CloakBrowser Stealth 上傳 (PIXTA / Freepik)
├── config.example.yaml
├── prompts_50.txt              # 50 個商用 prompt 範本
├── gen_metadata.py             # 圖片批次優化與 metadata 重新產生工具
├── run_50.sh                   # 50 張批次生圖與優化腳本
└── README.md
```

## 圖庫發布方式支援

| 平台 | 網頁自動化 (CloakBrowser) | FTP / FTPS 上傳 | 說明 |
|------|---------------------------|-----------------|------|
| **Adobe Stock** | ✅ 支援自動填寫欄位與 AI 標籤 | ❌ 官方已不活躍 | 推薦使用 Web 模式或 CSV 導入 |
| **Freepik** | ✅ 支援自動拖曳圖片 + CSV 一鍵導入 | ✅ 支援 FTPS (Explicit TLS) | 等級 3 以下帳號使用 Web 模式；等級 3 以上可用 FTPS |
| **PIXTA** | ✅ 支援網頁上傳與手動/Cookie 登入 | ❌ 官方不支援 FTP | 僅能使用瀏覽器上傳 |

## 隱私安全

- `config.yaml` 含有你的個人帳密 → 已加入 `.gitignore`
- Cookie 快取在 `.cookies/` → 已加入 `.gitignore`
- 產出圖片在 `output/` → 已加入 `.gitignore`

## 授權

MIT — Laban Chen
