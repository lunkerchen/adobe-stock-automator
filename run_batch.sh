#!/bin/bash
# Batch generate 10 stock images (bash v3 compatible)
set -e
ROOT="/Users/lunker/Projects/adobe-stock-automator"
OUTPUT="$ROOT/output"
WRAPPER="$ROOT/dashboard/scripts/codex-gen-wrapper.sh"
mkdir -p "$OUTPUT"

# Prompts inline - one per line
PROMPTS=(
"Modern business professionals collaborating in a bright minimalist office with large windows, natural light, white walls, wooden table, casual meeting"
"Futuristic digital technology concept with glowing blue circuit patterns, holographic interface, data streams, dark background, cyber atmosphere"
"Serene mountain lake landscape at golden hour, misty pine forest reflection, calm water, dramatic clouds, peaceful nature scene"
"Healthy colorful breakfast bowl with fresh fruits, granola, yogurt, berries, chia seeds on marble table, natural morning light"
"Peaceful yoga meditation session in sunlit minimalist room with large windows, wooden floor, plants, soft morning light, zen atmosphere"
"Tropical beach coastline at sunset with palm trees, golden sand, gentle waves, warm orange sky, vacation travel destination"
"Modern medical hospital room with advanced equipment, clean white interior, soft blue lighting, empty bed, healthcare concept"
"Abstract geometric patterns with flowing lines and vibrant gradient colors, modern art style, smooth curves, corporate abstract background"
"Online education concept with laptop, books, coffee cup on wooden desk, green plant, cozy study corner, soft lamp light"
"Modern city skyline at dusk with illuminated skyscrapers, twilight sky, reflection in river, urban architecture, dramatic clouds"
)

PIDS=()
for i in {0..9}; do
  TS=$(date +%s%3N)
  OUTFILE="$OUTPUT/ads_${TS}_${i}.jpg"
  echo "[$i] Starting: ${PROMPTS[$i]:0:50}..."
  bash "$WRAPPER" "${PROMPTS[$i]}" "$OUTFILE" 180 > "$OUTPUT/gen_${i}.log" 2>&1 &
  PIDS[$i]=$!
  sleep 2
done

echo "--- Waiting for all 10 generations to complete ---"
FAIL=0
for i in {0..9}; do
  wait ${PIDS[$i]}
  RC=$?
  LOGFILE="$OUTPUT/gen_${i}.log"
  RESULT=$(tail -1 "$LOGFILE" 2>/dev/null)
  if [ $RC -eq 0 ] && echo "$RESULT" | grep -q "^OK:"; then
    echo "[$i] DONE: $RESULT"
  else
    echo "[$i] FAIL (rc=$RC): $RESULT"
    FAIL=$((FAIL+1))
  fi
done

echo "--- Complete: $((10-FAIL))/10 succeeded, $FAIL failed ---"
ls -lh "$OUTPUT"/ads_*.jpg 2>/dev/null
