# REG3 Unified - IDML/XLSX Processing Pipeline

> Transform FAAC product catalog IDML files into structured XLSX with automated validation and continuous learning.

## Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/youruser/reg3-unified.git
cd reg3-unified
pip install -r requirements.txt
```

### 2. Add Files to Process

**With reference (for learning):**
```bash
cp catalog.idml input/idml/learning/
cp reference.xlsx input/xlsx/learning/
```

**Without reference (production):**
```bash
cp catalog.idml input/idml/batch/
```

### 3. Process with Claude Code

Push to GitHub, then in Claude Code:
```
> Process all IDML files and generate reports
```

### 4. Review Results
```bash
git pull
open reports/summary.html
```

## Workflow Diagram

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│   IDML   │────▶│ Extract  │────▶│ Compare  │────▶│ Report   │
│  Files   │     │   Data   │     │   vs     │     │ Results  │
└──────────┘     └──────────┘     │Reference │     └──────────┘
                                  └────┬─────┘
                                       │
                                       ▼
                                 ┌──────────┐
                                 │  Learn   │
                                 │  & Fix   │
                                 └──────────┘
```

## Project Status

| Metric | Current | Target |
|--------|---------|--------|
| Learning Files | 14 | - |
| Test Files | 141 | - |
| Accuracy | 85.81% | 99%+ |

## File Structure

```
reg3-unified/
├── input/           # Your IDML + reference XLSX
├── output/          # Generated XLSX
├── reports/         # Comparison reports
├── knowledge/       # Learning rules
├── src/             # Processing code
└── CLAUDE.md        # Instructions for Claude
```

## Key Commands

| Command | Description |
|---------|-------------|
| `./scripts/run_all.sh` | Full pipeline |
| `./scripts/run_import.sh` | Extract only |
| `./scripts/run_check.sh` | Compare only |

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - Full system design
- [CLAUDE.md](CLAUDE.md) - Claude Code instructions
- [knowledge/EXTRACTION_RULES.md](knowledge/EXTRACTION_RULES.md) - Pattern docs

## License
Proprietary - FAAC internal use
