# Claude Code Instructions - REG3 Unified Pipeline

## Project Purpose
Extract product data from FAAC IDML catalog files, compare with reference XLSX, and continuously improve accuracy through a learning feedback loop.

## On Repository Access

### 1. Check for New Input Files
```bash
# List new IDML files
ls -la input/idml/learning/*.idml 2>/dev/null
ls -la input/idml/batch/*.idml 2>/dev/null

# List reference files
ls -la input/xlsx/learning/*.xlsx 2>/dev/null
```

### 2. Read Knowledge Base First
Before any processing, read these files to understand current rules:
- `knowledge/EXTRACTION_RULES.md` - Pattern documentation
- `knowledge/field_mappings.json` - IDML → XLSX column mappings
- `knowledge/error_patterns.json` - Known issues and fixes
- `knowledge/corrections_log.json` - History of human corrections

### 3. Run Processing Pipeline

```bash
# Full pipeline
./scripts/run_all.sh

# Or step by step:
cd src/import && python main.py --input ../../input/idml --output ../../output/xlsx
cd src/check && python main.py --extracted ../../output/xlsx/learning --reference ../../input/xlsx/learning
```

### 4. Generate Reports
- Create `reports/summary.html` with overall stats
- Create individual reports in `reports/per-file/`

### 5. Commit Results
```bash
git add output/ reports/ knowledge/
git commit -m "Processed: [count] files, [accuracy]% accuracy"
git push
```

## File Processing Rules

### IDML Extraction Priorities
1. **Category** - From styled text "AUTOMAZIONI PER CANCELLI", "BARRIERE", etc.
2. **Product Name** - Main title with model number
3. **Page Numbers** - From filename and spread metadata
4. **Technical Specs** - From tables with "Caratteristiche tecniche" header
5. **SKU Codes** - Pattern: `[digits]` or alphanumeric codes
6. **Accessories** - Lists under "Accessori" or "Optional"

### Field Mapping Reference

#### prodotti sheet (36 columns)
| Column | Source |
|--------|--------|
| category | ParagraphStyle 'categoria' |
| name | ParagraphStyle 'titolo_prodotto' |
| page | Filename + Spread/@PageCount |
| description | Content after title, before table |

#### sku sheet (66 columns)
| Column | Table Header |
|--------|--------------|
| voltage | "Alimentazione" |
| motor_type | "Tipo di motore" |
| power | "Potenza max assorbita" |
| weight | "Peso" |
| dimensions | "Dimensioni" |

## Error Handling

### Common Issues
1. **Missing columns** - Check `knowledge/error_patterns.json` for column shift patterns
2. **Typos** - Check `knowledge/vocabulary.json` for known corrections
3. **Empty cells** - May be intentional (N/A) or extraction failure

### When Extraction Fails
1. Log error to `output/errors/[filename].log`
2. Include IDML structure dump for debugging
3. Continue with remaining files

## Learning Mode

### When Reference Files Exist
1. Extract IDML → Generated XLSX
2. Load Reference XLSX
3. Compare cell by cell
4. Log matches/mismatches/new/missing
5. If accuracy < 95%, flag for human review

### When Human Corrections Are Found
If `knowledge/corrections_log.json` has new entries:
1. Parse correction rules
2. Apply to extraction logic
3. Re-run affected files
4. Verify improvement

## Output Format

### Summary Report (HTML)
```html
<h1>REG3 Processing Summary</h1>
<p>Date: {timestamp}</p>
<p>Files Processed: {count}</p>
<p>Overall Accuracy: {percent}%</p>

<table>
  <tr><th>File</th><th>Accuracy</th><th>Matches</th><th>Mismatches</th></tr>
  {per-file rows}
</table>
```

### Per-File Report (JSON)
```json
{
  "file": "B614",
  "timestamp": "2024-12-15T10:30:00Z",
  "accuracy": 92.5,
  "matches": 148,
  "mismatches": 12,
  "new_fields": 3,
  "missing_fields": 0,
  "details": [
    {
      "sheet": "sku",
      "row": 3,
      "column": "voltage",
      "extracted": "220-240V~ 50/60 H",
      "expected": "220-240V~ 50/60 Hz",
      "status": "mismatch"
    }
  ]
}
```

## Git Commit Message Format

```
[type]: [summary]

Files: [count]
Accuracy: [percent]%
Changes: [brief description]
```

Types:
- `process`: Standard processing run
- `fix`: Applied correction from knowledge base
- `learn`: Updated extraction rules
- `error`: Failed processing (with reason)

## Quick Reference

### Process Single File
```bash
python src/import/main.py --file input/idml/learning/B614.idml --output output/xlsx/
```

### Compare Single File
```bash
python src/check/main.py --extracted output/xlsx/learning/B614.xlsx --reference input/xlsx/learning/B614.xlsx
```

### Update Knowledge Base
```bash
python src/learn/pattern_learner.py --corrections knowledge/corrections_log.json
```

### Generate All Reports
```bash
python src/check/reporter.py --input reports/per-file/ --output reports/summary.html
```
