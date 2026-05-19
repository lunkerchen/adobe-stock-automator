#!/bin/bash
# codex-gen-wrapper.sh — 用 Codex CLI (ChatGPT 訂閱) 生圖
# Usage: codex-gen-wrapper.sh <prompt> <output_path> [timeout_seconds]
set -e
PROMPT="$1"
OUTPUT="$2"
TIMEOUT="${3:-120}"
WORKDIR=$(mktemp -d /tmp/codex-gen-XXXXXX)
cd "$WORKDIR"
git init -q

# Run codex exec with script(1) to fake a PTY
script -q /dev/null timeout "$TIMEOUT" codex exec --yolo "Generate ONE photorealistic AI image. Prompt: $PROMPT. Do NOT write code. Save the image to $OUTPUT and print the path. Say nothing else." </dev/null 2>&1 | tail -5

# Also try to find image in Codex's generated_images dir
CODEX_IMG_DIR="$HOME/.codex/generated_images"
if [ ! -f "$OUTPUT" ] && [ -d "$CODEX_IMG_DIR" ]; then
  NEWEST=$(ls -1t "$CODEX_IMG_DIR" 2>/dev/null | head -1)
  if [ -n "$NEWEST" ]; then
    IMG_FILE=$(ls -1t "$CODEX_IMG_DIR/$NEWEST/"*.png 2>/dev/null | head -1)
    if [ -n "$IMG_FILE" ]; then
      cp "$IMG_FILE" "$OUTPUT"
    fi
  fi
fi

# Cleanup
rm -rf "$WORKDIR"

if [ -f "$OUTPUT" ]; then
  echo "OK:$OUTPUT"
  exit 0
else
  echo "FAIL:no output image generated"
  exit 1
fi
