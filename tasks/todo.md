# Todo

## 2026-05-20 chatgpt-web-gen provider

- [x] 釐清既有生圖 provider 接點與 chatgpt-web-gen CLI 輸出格式 -> 驗證: 找到 dashboard API provider 分流、UI provider config、`IMAGE:` 輸出格式。
- [x] 在 dashboard 生圖流程加入 `chatgpt-web-gen` 選項 -> 驗證: UI provider 下拉選單可選，API 透過 `main.py generate -p chatgpt-web-gen` 呼叫 `/Users/lunker/Developer/Projects/chatgpt-web-gen/gen.py`。
- [x] 補上最小文件或設定提示 -> 驗證: README 已標明需先在 chatgpt-web-gen 執行 `python gen.py --login`，且使用 CLI 不是 TG Bot。
- [x] 執行靜態檢查或可用測試 -> 驗證: Python 編譯通過、TypeScript noEmit 通過；dashboard lint 受既有問題阻擋，詳見 Review。

## Review

- 已新增 Python provider `chatgpt-web-gen`，呼叫本機 `/Users/lunker/Developer/Projects/chatgpt-web-gen/gen.py`，解析 `IMAGE:` 輸出並轉存為本專案 JPEG。
- 已在 dashboard provider 設定與 Config 頁預設供應商清單加入 `chatgpt-web-gen`。
- 已更新 README 與 `config.example.yaml`，說明直接使用 chatgpt-web-gen CLI，需先完成 `python gen.py --login`。
- 驗證結果：`python3 -m py_compile src/generate.py main.py` 通過；`npx tsc --noEmit` 通過；`get_generator("chatgpt-web-gen")` 回傳 `ChatGPTWebGenGenerator`。
- `npm run lint` 未通過，錯誤來自既有檔案規則問題：`dashboard/src/app/api/generate/route.ts` 的 `require()/any`、`ConfigPanel.tsx` 與 `GeneratePanel.tsx` 的 effect 內同步 setState、`ImageGallery.tsx` 的 render 中 `Date.now()` 等。

## 2026-05-20 push chatgpt-web-gen provider

- [x] 確認待提交檔案只包含新增生圖流程相關內容 -> 驗證: `git status --short` 與 diff 無 output 圖片/CSV。
- [x] 重新執行最小驗證 -> 驗證: Python 編譯與 dashboard TypeScript 檢查通過。
- [x] 建立 commit 並推送到 GitHub -> 驗證: `git push origin main` 成功，commit `ad54940` 已推到 `origin/main`。
