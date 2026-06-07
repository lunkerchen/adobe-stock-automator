#!/bin/bash
# Batch generate 50 stock images - 5 rounds of 10 parallel
# bash v3 compatible (no mapfile, no associative arrays)
set -e
ROOT="/Users/lunker/Projects/adobe-stock-automator"
OUTPUT="$ROOT/output"
WRAPPER="$ROOT/dashboard/scripts/codex-gen-wrapper.sh"
PROMPTS_FILE="$ROOT/prompts_50.txt"
mkdir -p "$OUTPUT"

# Read prompts line by line into array (bash v3 compatible)
PROMPTS=()
while IFS= read -r line; do
  [ -n "$line" ] && PROMPTS+=("$line")
done < "$PROMPTS_FILE"

TOTAL=${#PROMPTS[@]}
echo "Total prompts: $TOTAL"

BATCH_SIZE=10
GLOBAL_FAIL=0
GLOBAL_DONE=0

for ((batch=0; batch<TOTAL; batch+=BATCH_SIZE)); do
  end=$((batch + BATCH_SIZE))
  [ $end -gt $TOTAL ] && end=$TOTAL
  BATCH_NUM=$((batch / BATCH_SIZE + 1))
  echo ""
  echo "============================================================"
  echo "  BATCH $BATCH_NUM / $(( (TOTAL+BATCH_SIZE-1)/BATCH_SIZE ))  (prompts $((batch+1))-$end)"
  echo "============================================================"

  PIDS=()
  for ((i=batch; i<end; i++)); do
    TS=$(date +%s%3N)
    OUTFILE="$OUTPUT/stock_${TS}_$((i-batch)).jpg"
    echo "  [$i] Starting: ${PROMPTS[$i]:0:60}..."
    bash "$WRAPPER" "${PROMPTS[$i]}" "$OUTFILE" 180 > "$OUTPUT/gen_${i}.log" 2>&1 &
    PIDS[$i]=$!
    sleep 1
  done

  # Wait for this batch
  for ((i=batch; i<end; i++)); do
    wait ${PIDS[$i]}
    RC=$?
    LOGFILE="$OUTPUT/gen_${i}.log"
    RESULT=$(tail -1 "$LOGFILE" 2>/dev/null)
    if [ $RC -eq 0 ] && echo "$RESULT" | grep -q "^OK:"; then
      GLOBAL_DONE=$((GLOBAL_DONE+1))
      echo "  [$i] OK"
    else
      GLOBAL_FAIL=$((GLOBAL_FAIL+1))
      echo "  [$i] FAIL (rc=$RC): $RESULT"
    fi
  done

  echo "  Batch $BATCH_NUM done: $((GLOBAL_DONE+GLOBAL_FAIL))/$TOTAL total"
done

echo ""
echo "============================================================"
echo "  COMPLETE: $GLOBAL_DONE/$TOTAL succeeded, $GLOBAL_FAIL failed"
echo "============================================================"
ls -lh "$OUTPUT"/stock_*.jpg 2>/dev/null | wc -l
