# REG3 Unified - IDML/XLSX Processing Pipeline

## Vision: Positive Learning Feedback Loop

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         YOUR LOCAL MACHINE                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────────────────┐  │
│  │   IDML      │    │   XLSX      │    │    Git Repository               │  │
│  │   Files     │───▶│   Reference │───▶│    (GitHub)                     │  │
│  │   (Source)  │    │   (Truth)   │    │    ├── input/                   │  │
│  └─────────────┘    └─────────────┘    │    │   ├── idml/                │  │
│                                        │    │   └── xlsx/                │  │
│                                        │    ├── output/                  │  │
│                                        │    ├── reports/                 │  │
│                                        │    └── knowledge/               │  │
│                                        └────────────┬────────────────────┘  │
└─────────────────────────────────────────────────────│───────────────────────┘
                                                      │
                                                      │ git push
                                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CLAUDE CODE (Cloud)                                 │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    PROCESSING PIPELINE                               │   │
│  │                                                                      │   │
│  │   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐         │   │
│  │   │ 1.PARSE │───▶│ 2.EXTR  │───▶│3.COMPAR │───▶│4.REPORT │         │   │
│  │   │ IDML    │    │ ACT     │    │ E/CHECK │    │         │         │   │
│  │   └─────────┘    └─────────┘    └─────────┘    └─────────┘         │   │
│  │        │              │              │              │               │   │
│  │        ▼              ▼              ▼              ▼               │   │
│  │   XML/Stories   prodotti.xlsx  Match/Mismatch   HTML/JSON/CSV      │   │
│  │                 sku.xlsx       New/Missing                          │   │
│  │                                                                      │   │
│  │   ┌─────────────────────────────────────────────────────────────┐   │   │
│  │   │              5. LEARNING ENGINE                              │   │   │
│  │   │   ┌──────────────────────────────────────────────────────┐  │   │   │
│  │   │   │ knowledge/                                            │  │   │   │
│  │   │   │ ├── EXTRACTION_RULES.md    (Pattern library)         │  │   │   │
│  │   │   │ ├── FIELD_MAPPINGS.json    (IDML → XLSX mapping)     │  │   │   │
│  │   │   │ ├── ERROR_PATTERNS.json    (Known issues)            │  │   │   │
│  │   │   │ └── CORRECTIONS_LOG.json   (Human corrections)       │  │   │   │
│  │   │   └──────────────────────────────────────────────────────┘  │   │   │
│  │   └─────────────────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│                                   │                                         │
│                                   │ git commit + push                       │
│                                   ▼                                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ git pull
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         YOUR LOCAL MACHINE                                  │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │   Download Results:                                                  │   │
│  │   • output/*.xlsx       - Extracted spreadsheets                     │   │
│  │   • reports/*.html      - Visual comparison reports                  │   │
│  │   • knowledge/*.json    - Updated extraction rules                   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │   HUMAN REVIEW LOOP:                                                 │   │
│  │   1. Review reports/*.html                                           │   │
│  │   2. Fix mismatches in xlsx/ reference files OR                      │   │
│  │   3. Correct extraction rules in knowledge/                          │   │
│  │   4. Push corrections → Claude learns from them                      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## The Feedback Loop in Action

### Cycle 1: Initial Processing
```
You: git push (14 IDML + 14 reference XLSX)
Claude: Extract → Compare → 85.81% accuracy
Claude: Generate reports showing 14.19% errors
Claude: git push results
You: git pull → Review errors
```

### Cycle 2: Correction Phase
```
You: Fix reference XLSX or document extraction rules
You: git push corrections
Claude: Re-run extraction with updated rules
Claude: Compare → 92% accuracy (improved!)
Claude: Update knowledge/CORRECTIONS_LOG.json
Claude: git push
```

### Cycle 3+: Continuous Improvement
```
Each cycle:
- Accuracy improves
- Knowledge base grows
- Edge cases get documented
- Eventually: 99%+ accuracy
```

## Repository Structure

```
reg3-unified/
├── README.md                    # Quick start guide
├── ARCHITECTURE.md              # This file
│
├── input/                       # 🔹 YOU PUT FILES HERE
│   ├── idml/                    # IDML files to process
│   │   ├── learning/            # Paired with references (for training)
│   │   └── batch/               # Production files (no reference)
│   └── xlsx/                    # Reference XLSX files (ground truth)
│       └── learning/            # Matches idml/learning/ filenames
│
├── output/                      # 🔹 CLAUDE GENERATES HERE
│   ├── xlsx/                    # Extracted spreadsheets
│   │   ├── learning/            # From idml/learning/
│   │   └── batch/               # From idml/batch/
│   └── errors/                  # Failed extractions with logs
│
├── reports/                     # 🔹 COMPARISON RESULTS
│   ├── summary.html             # Dashboard of all results
│   ├── per-file/                # Individual file reports
│   │   ├── B614.html
│   │   ├── B614.json
│   │   └── ...
│   └── history/                 # Past run archives
│
├── knowledge/                   # 🔹 LEARNING ENGINE
│   ├── EXTRACTION_RULES.md      # Human-readable patterns
│   ├── field_mappings.json      # IDML field → XLSX column
│   ├── error_patterns.json      # Known issues & fixes
│   ├── corrections_log.json     # Human corrections history
│   └── vocabulary.json          # Domain terms, typo fixes
│
├── src/                         # 🔹 PROCESSING CODE
│   ├── import/                  # IDML → XLSX extraction
│   │   ├── idml_parser.py
│   │   ├── table_extractor.py
│   │   ├── text_extractor.py
│   │   ├── xlsx_writer.py
│   │   └── main.py
│   ├── check/                   # XLSX vs Reference comparison
│   │   ├── xlsx_loader.py
│   │   ├── comparator.py
│   │   ├── reporter.py
│   │   └── main.py
│   └── learn/                   # Knowledge update logic
│       ├── pattern_learner.py
│       └── correction_applier.py
│
├── scripts/                     # 🔹 AUTOMATION
│   ├── run_all.sh               # Full pipeline
│   ├── run_import.sh            # Only extraction
│   ├── run_check.sh             # Only comparison
│   └── run_learn.sh             # Only learning update
│
├── CLAUDE.md                    # Instructions for Claude Code
└── .github/
    └── workflows/
        └── process.yml          # Optional: GitHub Actions automation
```

## Key Files Explained

### CLAUDE.md - Instructions for Claude
This file tells Claude Code exactly what to do when it opens the repo:

```markdown
# Claude Instructions for REG3

## On Repository Open
1. Check input/idml/ for new files
2. Run extraction pipeline
3. Compare with references if available
4. Generate reports
5. Update knowledge base if corrections found
6. Commit and push results

## Commands
- `process`: Full pipeline
- `extract`: IDML → XLSX only
- `check`: Compare with references
- `learn`: Update knowledge from corrections
```

### knowledge/field_mappings.json
Maps IDML patterns to XLSX columns:

```json
{
  "prodotti": {
    "category": {
      "patterns": ["AUTOMAZIONI PER CANCELLI", "BARRIERE STRADALI"],
      "xpath": "//CharacterStyleRange[@AppliedCharacterStyle='categoria']"
    },
    "name": {
      "patterns": ["regex: ^[A-Z0-9]+ .*"],
      "xpath": "//ParagraphStyleRange[@AppliedParagraphStyle='titolo_prodotto']"
    }
  },
  "sku": {
    "voltage": {
      "patterns": ["230V~", "400V 3~", "24V"],
      "table_header": "Alimentazione"
    }
  }
}
```

### knowledge/corrections_log.json
Tracks human corrections for learning:

```json
{
  "corrections": [
    {
      "date": "2024-12-15",
      "file": "B614",
      "field": "condensatore_spunto",
      "extracted": null,
      "expected": "25 µF",
      "rule_update": "Add column mapping for 'Condensatore spunto'"
    },
    {
      "date": "2024-12-15", 
      "file": "746_C",
      "field": "voltage",
      "extracted": "220-240V~ 50/60 H",
      "expected": "220-240V~ 50/60 Hz",
      "rule_update": "Typo correction: 'H' → 'Hz' at end of voltage string"
    }
  ]
}
```

## Workflow Commands

### Your Side (Local)

```bash
# Clone repo (first time)
git clone https://github.com/youruser/reg3-unified.git
cd reg3-unified

# Add new IDML files for processing
cp ~/FAAC/catalogs/*.idml input/idml/batch/

# Add learning pairs (IDML + reference XLSX)
cp catalog_B614.idml input/idml/learning/
cp 160-163_B614.xlsx input/xlsx/learning/

# Push to trigger Claude
git add .
git commit -m "Add B614 for processing"
git push

# After Claude processes...
git pull

# Review results
open reports/summary.html
```

### Claude's Side (Cloud)

Claude Code sees the repo and runs:

```bash
# Automated on push or manual trigger
./scripts/run_all.sh

# Which does:
# 1. Extract all IDML files
python src/import/main.py --input input/idml --output output/xlsx

# 2. Compare learning files with references
python src/check/main.py --extracted output/xlsx/learning --reference input/xlsx/learning --reports reports/per-file

# 3. Generate summary report
python src/check/reporter.py --summary reports/summary.html

# 4. Apply any corrections found in knowledge/
python src/learn/correction_applier.py

# 5. Commit results
git add output/ reports/ knowledge/
git commit -m "Processed: 14 files, 85.81% accuracy"
git push
```

## Getting Started

### Step 1: Create GitHub Repository

```bash
# Create new repo on github.com
# Then locally:
git clone https://github.com/youruser/reg3-unified.git
cd reg3-unified
```

### Step 2: Initialize Structure

```bash
mkdir -p input/{idml/{learning,batch},xlsx/learning}
mkdir -p output/{xlsx/{learning,batch},errors}
mkdir -p reports/{per-file,history}
mkdir -p knowledge
mkdir -p src/{import,check,learn}
mkdir -p scripts
```

### Step 3: Copy Your Existing Code

From your current projects:
```bash
# From import project
cp import/src/*.py src/import/

# From check project
cp check/src/*.py src/check/
```

### Step 4: Add CLAUDE.md

Create `CLAUDE.md` with processing instructions.

### Step 5: Push and Let Claude Process

```bash
git add .
git commit -m "Initial setup"
git push
```

Open Claude Code, open the repo, and say:
> "Process all IDML files in input/ and generate reports"

## Success Metrics

| Metric | Initial | Target |
|--------|---------|--------|
| Extraction Accuracy | 85.81% | 99%+ |
| Manual Review Time | Hours | Minutes |
| New File Processing | Manual | Automated |
| Error Recovery | Ad-hoc | Systematic |

## FAQ

**Q: How does Claude "learn" from corrections?**
A: When you fix a reference XLSX or add rules to `knowledge/`, Claude reads these on the next run and applies them. The `corrections_log.json` grows with each fix, creating a searchable history.

**Q: Can I process files without references?**
A: Yes! Put IDML files in `input/idml/batch/`. Claude will extract them but skip comparison. Use this for production files after accuracy is proven.

**Q: What if Claude makes the same mistake repeatedly?**
A: Add the pattern to `knowledge/error_patterns.json` with the fix. Claude will apply it automatically.

**Q: How do I handle edge cases?**
A: Document them in `knowledge/EXTRACTION_RULES.md` with examples. Claude reads this file before each extraction.
