# IDML to XLSX Extraction Rules

## Overview
This document contains the patterns and rules for extracting product data from FAAC IDML catalog files. Claude reads this before each extraction run.

---

## Product Categories

### Detection Pattern
Look for ParagraphStyleRange with style containing "categoria" or "category":
- `AUTOMAZIONI PER CANCELLI SCORREVOLI`
- `AUTOMAZIONI PER CANCELLI A BATTENTE`  
- `BARRIERE STRADALI`
- `AUTOMAZIONI PER PORTE SEZIONALI E BASCULANTI`

### Category Normalization
| Raw IDML | Normalized |
|----------|------------|
| AUTOMAZIONI PER CANCELLI SCORREVOLI | Cancelli Scorrevoli |
| AUTOMAZIONI PER CANCELLI A BATTENTE | Cancelli a Battente |
| BARRIERE STRADALI | Barriere |
| BARRIERE AUTOMATICHE | Barriere |

---

## Product Name Extraction

### Pattern
Title is typically:
1. First large text after category
2. Contains model number (e.g., "B614", "746 C", "620 Standard")
3. May have subtitle/description

### Examples
```
746 C – Operatore oleodinamico interrato
B614 – Barriera automatica
620 Standard – Automazione per porte garage
```

### Rules
- Model number always first
- Separator: ` – ` (en-dash with spaces) or ` - ` (hyphen)
- Description follows

---

## Technical Specifications Table

### Table Detection
Look for tables with header row containing:
- "Caratteristiche tecniche" (Technical characteristics)
- OR first column headers like "Alimentazione", "Potenza", etc.

### Column Mapping (sku sheet)

| Table Header (Italian) | XLSX Column | Notes |
|------------------------|-------------|-------|
| Alimentazione | voltage | e.g., "230V~ 50/60Hz" |
| Tipo di motore | motor_type | e.g., "Brushless", "Asincrono" |
| Potenza max assorbita | power | e.g., "300 W" |
| Coppia max | torque | e.g., "15 Nm" |
| Peso | weight | e.g., "8.5 kg" |
| Dimensioni (L×P×H) | dimensions | e.g., "330×205×290 mm" |
| Grado di protezione | ip_rating | e.g., "IP44" |
| Temperatura funzionamento | temperature | e.g., "-20°C ÷ +55°C" |
| N° max cicli/ora | cycles_hour | e.g., "25" |
| N° max cicli/giorno | cycles_day | e.g., "400" |
| Velocità | speed | e.g., "0.25 m/s" |
| Corsa max | max_stroke | e.g., "1.8 m" |
| Condensatore marcia | capacitor_run | e.g., "12 µF" |
| Condensatore spunto | capacitor_start | e.g., "25 µF" |
| Finecorsa | limit_switch | e.g., "Encoder" |
| Sblocco | release | e.g., "A chiave" |
| Centrale | control_unit | e.g., "E145" |

### Multi-row Products
Some products have multiple SKU variants in same table:
- Each row = different SKU
- Share same product metadata
- Different technical specs

---

## SKU Code Extraction

### Pattern Recognition
```regex
# Standard format
\d{6,7}          # 6-7 digits: 104610, 1047003

# With suffix
\d{6,7}[A-Z]*    # Digits + letters: 104610H, 1047003BPR

# Kit format
\d{6,7}\s+KIT    # 104610 KIT
```

### Location
SKUs typically found:
1. In table as row identifier (first column)
2. In accessory lists
3. In "Codice" column

---

## Accessory Lists

### Detection
Look for sections titled:
- "Accessori"
- "Optional"
- "Accessori e ricambi"

### Structure
```
Accessory Name          SKU
─────────────────────────────────
Lampeggiatore LED      410013
Fotocellula XP 20      785104
```

### Rules
- Extract accessory name + SKU pair
- Associate with parent product
- Multiple accessories per product

---

## Known Typos & Corrections

Apply these corrections automatically:

| Found | Correct |
|-------|---------|
| `50/60 H` | `50/60 Hz` |
| `Scheda eletttronica` | `Scheda elettronica` |
| `Contentore` | `Contenitore` |
| `Interfaccia US` | `Interfaccia BUS` |
| `amortizzati` | `ammortizzati` |
| `Cilidro` | `Cilindro` |

---

## Page Number Extraction

### From Filename
Pattern: `Pages_XXX-YYY_ProductName.idml`
```
Pages_160-163_B614.idml → pages: 160-163
```

### From Spread Metadata
In `designmap.xml`:
```xml
<idPkg:Spread src="Spreads/Spread_u123.xml"/>
```

Check spread for `@PageCount` and page items.

---

## Empty/Missing Values

### When to Use Empty String
- Field not applicable to product type
- Information genuinely not provided in source

### When to Flag as Error
- Field exists in IDML but extraction failed
- Unexpected structure change

---

## Product Type Specific Rules

### Gate Operators (Cancelli)
- Always has: voltage, motor_type, max_stroke
- Optional: encoder, photocell compatibility

### Barriers (Barriere)
- Always has: voltage, cycles_hour, arm_length
- Special: arm specifications, LED options

### Garage Doors (Sezionali)
- Always has: voltage, power, door_dimensions
- Special: spring compensation, safety features

---

## Validation Rules

### Numeric Fields
- Voltage: Must contain V, ~, Hz
- Power: Must end with W, kW
- Weight: Must end with kg, g
- Temperature: Must contain °C

### Required Fields per Product
```json
{
  "prodotti": ["category", "name", "page"],
  "sku": ["sku_code", "voltage"]
}
```

---

## Change Log

| Date | Change | Reason |
|------|--------|--------|
| 2024-12-15 | Added capacitor_start column | Missing from B614 |
| 2024-12-15 | Added Hz typo correction | Found in 746 C |
| 2024-12-14 | Initial documentation | Project start |
