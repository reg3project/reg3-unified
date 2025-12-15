#!/bin/bash
# REG3 Unified - Full Processing Pipeline
# Usage: ./scripts/run_all.sh

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo "REG3 Unified Pipeline"
echo "Started: $(date)"
echo "========================================"

cd "$PROJECT_ROOT"

# Step 1: Check for input files
echo ""
echo "[1/5] Checking input files..."
LEARNING_IDML=$(find input/idml/learning -name "*.idml" 2>/dev/null | wc -l)
BATCH_IDML=$(find input/idml/batch -name "*.idml" 2>/dev/null | wc -l)
REFERENCE_XLSX=$(find input/xlsx/learning -name "*.xlsx" 2>/dev/null | wc -l)

echo "  Learning IDML files: $LEARNING_IDML"
echo "  Batch IDML files: $BATCH_IDML"
echo "  Reference XLSX files: $REFERENCE_XLSX"

if [ "$LEARNING_IDML" -eq 0 ] && [ "$BATCH_IDML" -eq 0 ]; then
    echo "  WARNING: No IDML files found to process"
    exit 0
fi

# Step 2: Run extraction
echo ""
echo "[2/5] Running IDML extraction..."

# Process learning files
if [ "$LEARNING_IDML" -gt 0 ]; then
    echo "  Processing $LEARNING_IDML learning files..."
    python src/import/main.py \
        --input input/idml/learning \
        --output output/xlsx/learning \
        --knowledge knowledge/field_mappings.json \
        2>&1 | tee -a output/extraction.log
fi

# Process batch files
if [ "$BATCH_IDML" -gt 0 ]; then
    echo "  Processing $BATCH_IDML batch files..."
    python src/import/main.py \
        --input input/idml/batch \
        --output output/xlsx/batch \
        --knowledge knowledge/field_mappings.json \
        2>&1 | tee -a output/extraction.log
fi

# Step 3: Run comparison (only for learning files with references)
echo ""
echo "[3/5] Running comparison with references..."

if [ "$LEARNING_IDML" -gt 0 ] && [ "$REFERENCE_XLSX" -gt 0 ]; then
    python src/check/main.py \
        --extracted output/xlsx/learning \
        --reference input/xlsx/learning \
        --reports reports/per-file \
        2>&1 | tee -a reports/comparison.log
    
    # Extract accuracy from log
    ACCURACY=$(grep "Overall accuracy" reports/comparison.log | tail -1 | grep -oP '\d+\.\d+' || echo "N/A")
    echo "  Overall accuracy: ${ACCURACY}%"
else
    echo "  Skipping comparison (no reference files)"
    ACCURACY="N/A"
fi

# Step 4: Generate summary report
echo ""
echo "[4/5] Generating summary report..."
python src/check/reporter.py \
    --input reports/per-file \
    --output reports/summary.html \
    2>&1

echo "  Report saved: reports/summary.html"

# Step 5: Update knowledge base
echo ""
echo "[5/5] Checking for knowledge updates..."

# Check if corrections_log has been manually updated
if [ -f "knowledge/corrections_log.json" ]; then
    PENDING=$(python -c "import json; data=json.load(open('knowledge/corrections_log.json')); print(sum(1 for c in data.get('corrections',[]) if not c.get('applied')))" 2>/dev/null || echo "0")
    
    if [ "$PENDING" -gt 0 ]; then
        echo "  Found $PENDING pending corrections to apply"
        python src/learn/correction_applier.py \
            --corrections knowledge/corrections_log.json \
            --mappings knowledge/field_mappings.json
    else
        echo "  No pending corrections"
    fi
fi

# Final summary
echo ""
echo "========================================"
echo "Pipeline Complete"
echo "========================================"
echo "  Files processed: $((LEARNING_IDML + BATCH_IDML))"
echo "  Accuracy: ${ACCURACY}%"
echo "  Summary: reports/summary.html"
echo "  Finished: $(date)"
echo "========================================"

# Prepare git commit message
COMMIT_MSG="process: $((LEARNING_IDML + BATCH_IDML)) files, ${ACCURACY}% accuracy"
echo ""
echo "Suggested commit: git commit -m \"$COMMIT_MSG\""
