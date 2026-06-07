# Adobe Stock & Freepik Automator

AIストックイメージの自動生成、最適化、マルチプラットフォーム公開ツール。Codex CLI（ChatGPT サブスクリプション）または OpenAI/Stability/Replicate などの複数の画像生成エンジンをサポートし、Adobe Stock および Freepik の仕様に準拠した画像とメタデータを自動生成し、FTPS または CloakBrowser による自動ウェブアップロードを行います。

## パイプライン

```
プロンプト ──> AI 生成 ──> 6MP アップスケール ──> メタデータ CSV (Adobe / Freepik) ──> Web/FTP/FTPS 自動アップロード
```

## 機能

*   **マルチプラットフォーム CSV サポート**：
    *   **Adobe Stock**：カンマ区切り CSV を出力。カテゴリ名を Adobe Stock 規定の数値 ID に自動変換。
    *   **Freepik**：セミコロン (`;`) 区切り CSV を出力（フィールド：`File name;Title;Keywords;Prompt;Model`）。AI 生成コンテンツはキーワード末尾に自動で `_ai_generated` を付加。タイトル長は 100 文字以内に自動的に切り詰められ、エラーを防止。
*   **自動解像度最適化 (Upscale)**：画像の解像度を自動検出。6MP 未満の場合は Lanczos フィルターを使用して 6MP+ (3000x2000) にロスレス拡大し、ストックプラットフォームの審査を 100% 通過。
*   **堅牢なウェブ自動アップロード (CloakBrowser)**：Stealth Chromium を使用して Cloudflare のボット対策を回避。手動/クッキーログインの永続化、画像のドラッグ＆ドロップアップロードをサポート。専用 `metadata_freepik.csv` のワンクリックインポートで一括適用。
*   **安全な FTPS 接続**：Freepik レベル 3 以上のアカウント向け FTPS (Explicit TLS) 一括高速アップロードに対応。

## クイックスタート

```bash
# 依存関係のインストール
pip install -r requirements.txt

# 設定ファイルの初期化
cp config.example.yaml config.yaml
# config.yaml にストックアカウントの認証情報または API キーを記入

# 画像生成のテスト (API キー不要のダミーモード、Adobe と Freepik 両方の情報を生成)
python3 main.py generate "neon retro synthwave sunset" -n 1 -p dummy --freepik

# output ディレクトリ内の既存 JPEG 画像をすべてアップロード (Freepik ウェブアップロード例)
python3 main.py upload --platform freepik
```

## CLI コマンド

| コマンド | 説明 |
|---------|------|
| `generate` | AI 生成 → 6MP アップスケール → CSV 生成 → ウェブアップロード（`--freepik` で Freepik 出力も同時生成） |
| `upload` | CloakBrowser を使用して output ディレクトリ内の既存画像をすべてアップロード（adobe-stock, freepik 対応） |
| `cloak` | CloakBrowser による「生成＋ウェブ自動アップロード」統合ワークフロー |
| `portal_upload` | Adobe Stock Portal 専用アップロードモジュール |
| `batch` | プロンプトファイルの一括処理 |
| `requirements` | 各ストックプラットフォームの画像仕様を表示 |

### 一括生成（50 枚）

```bash
bash run_50.sh
```

`dashboard/scripts/codex-gen-wrapper.sh` を使用して Codex CLI による並列生成を実行。1バッチ10枚、約3〜5分で50枚を完了。
生成後は `./gen_metadata.py` を実行して全 CSV を再生成・更新。

## プロジェクト構成

```
adobe-stock-automator/
├── main.py                     # CLI エントリポイント (Click)
├── src/
│   ├── config.py               # YAML 設定読み込みと環境変数による上書き
│   ├── generate.py             # 画像生成 (dummy/openai/stability/replicate/local)
│   ├── image_utils.py          # 画像解像度検出と 6MP+ Lanczos 最適化
│   ├── metadata.py             # メタデータ生成と Adobe/Freepik デュアル CSV フォーマット出力
│   ├── upload.py               # FTP / FTPS (Explicit TLS) アップロードロジック
│   ├── submit_browser.py       # Playwright ブラウザ自動化
│   ├── portal_upload.py        # Adobe Portal 専用アップロード
│   └── upload_cloak.py         # CloakBrowser Stealth アップロード (Adobe Stock / Freepik)
├── config.example.yaml
├── prompts_50.txt              # 50 の商用プロンプトテンプレート
├── gen_metadata.py             # 画像一括最適化とメタデータ再生成ツール
├── run_50.sh                   # 50枚一括生成と最適化スクリプト
├── README.md                   # オリジナル (繁体字中国語)
├── README.en.md                # 英語
├── README.ja.md                # 日本語
├── README.ko.md                # 韓国語
├── README.es.md                # スペイン語
└── README.fr.md                # フランス語
```

## プラットフォーム対応

| プラットフォーム | ウェブ自動化 (CloakBrowser) | FTP / FTPS アップロード | 備考 |
|----------------|----------------------------|------------------------|------|
| **Adobe Stock** | ✅ 自動フィールド入力と AI タグ | ❌ 公式非活性 | Web モードまたは CSV インポート推奨 |
| **Freepik** | ✅ 自動ドラッグ＆ドロップ + CSV ワンクリックインポート | ✅ FTPS (Explicit TLS) 対応 | レベル 3 未満は Web モード、レベル 3 以上は FTPS 利用可能 |

## プライバシーとセキュリティ

- `config.yaml` には個人の認証情報が含まれます → `.gitignore` に追加済み
- Cookie キャッシュは `.cookies/` → `.gitignore` に追加済み
- 生成画像は `output/` → `.gitignore` に追加済み

## ライセンス

MIT — Laban Chen
