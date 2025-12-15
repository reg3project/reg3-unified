"""
Table Extractor - Extracts technical specifications from IDML tables

Handles various table formats found in FAAC catalogs and maps
table headers to standardized column names.
"""

import re
from typing import Dict, List, Optional, Tuple


class TableExtractor:
    """Extract and normalize table data from IDML."""

    # Header mappings (Italian -> standardized)
    HEADER_MAPPINGS = {
        # Voltage/Power
        'alimentazione': 'voltage',
        'tensione': 'voltage',
        'tensione di alimentazione': 'voltage',
        'tensione di alimentazione di rete': 'voltage',
        'supply voltage': 'voltage',
        'potenza max assorbita': 'power',
        'potenza max': 'power',
        'potenza': 'power',
        'power': 'power',

        # Motor
        'tipo di motore': 'motor_type',
        'motore elettrico': 'motor_type',
        'motore': 'motor_type',
        'motor type': 'motor_type',

        # Physical - Weight
        'peso': 'weight',
        'peso operatore': 'weight',
        'peso attuatore': 'weight',
        'peso motore': 'weight',
        'weight': 'weight',
        'peso max anta': 'max_gate_weight',
        'peso max anta cantilever': 'max_gate_weight_cantilever',
        'peso max': 'max_gate_weight',

        # Physical - Dimensions
        'dimensioni': 'dimensions',
        'dimensioni (lxpxh)': 'dimensions',
        'dimensioni operatore': 'dimensions',
        'dimensions': 'dimensions',
        'ingombri': 'dimensions',
        'ingombro': 'dimensions',

        # Performance - Speed
        'velocità': 'speed',
        'velocità max anta': 'speed',
        'velocità max stelo': 'speed',
        'velocità angolare max': 'speed',
        "velocità dell'anta": 'speed',
        'velocita anta': 'speed',
        'speed': 'speed',

        # Performance - Torque/Force
        'coppia max': 'torque',
        'coppia nominale': 'torque',
        'coppia': 'torque',
        'torque': 'torque',
        'forza max di spinta': 'max_force',
        'forza max': 'max_force',
        'forza di spinta': 'max_force',

        # Performance - Stroke/Length
        'corsa max': 'max_stroke',
        'corsa dello stelo': 'max_stroke',
        'corsa': 'max_stroke',
        'larghezza max': 'max_width',
        'larghezza max anta': 'max_width',
        'lunghezza max anta': 'max_length',
        'lunghezza max asta': 'max_length',
        'lunghezza max': 'max_length',
        'max stroke': 'max_stroke',

        # Cycles/Frequency
        'n° max cicli/ora': 'cycles_hour',
        'cicli/ora': 'cycles_hour',
        'frequenza di utilizzo': 'cycles_hour',
        'cycles/hour': 'cycles_hour',
        'n° max cicli/giorno': 'cycles_day',
        'cicli/giorno': 'cycles_day',
        'cycles/day': 'cycles_day',

        # Protection
        'grado di protezione': 'ip_rating',
        'ip': 'ip_rating',
        'protection': 'ip_rating',
        'temperatura funzionamento': 'temperature',
        'temperatura ambiente di esercizio': 'temperature',
        'temperatura': 'temperature',
        'operating temperature': 'temperature',
        'termoprotezione': 'thermal_protection',

        # Electrical
        'condensatore marcia': 'capacitor_run',
        'condensatore': 'capacitor_run',
        'condensatore spunto': 'capacitor_start',
        'condensatore di spunto': 'capacitor_start',
        'corrente assorbita': 'current',
        'corrente max assorbita': 'current',

        # Mechanical
        'pignone': 'pinion',
        'rapporto di riduzione': 'gear_ratio',
        'rapporto riduzione': 'gear_ratio',
        'angolo max apertura anta': 'max_angle',
        'angolo max apertura': 'max_angle',
        'spazio di fermata': 'stopping_space',
        'encoder': 'encoder',
        'encoder magnetico': 'encoder',
        'tipo di rallentamento': 'deceleration_type',
        'regolazione velocità e controllo motore': 'speed_control',
        'regolazione della forza': 'force_regulation',

        # Control
        'finecorsa': 'limit_switch',
        'fine corsa': 'limit_switch',
        'limit switch': 'limit_switch',
        'sblocco': 'release',
        'sblocco manuale': 'release',
        'dispositivo di sblocco': 'release',
        'manual release': 'release',
        'centrale': 'control_unit',
        'scheda elettronica': 'control_unit',
        'apparecchiatura elettronica': 'control_unit',
        'control unit': 'control_unit',

        # Materials
        'tipo di materiale': 'material_type',
        'tipo di trattamento': 'treatment_type',
        'tipo di olio': 'oil_type',
        'tipo di asta': 'arm_type',
        'staffe di fissaggio': 'mounting_brackets',
        'portata gruppo motore-pompa': 'pump_flow',

        # Identifiers
        'codice': 'sku_code',
        'modello': 'model',
        'code': 'sku_code',
    }

    def __init__(self, field_mappings: Optional[Dict] = None):
        """Initialize with optional custom field mappings."""
        self.field_mappings = field_mappings or {}
        self._load_custom_mappings()

    def _load_custom_mappings(self) -> None:
        """Load additional mappings from field_mappings config."""
        if 'sku' in self.field_mappings:
            for field, config in self.field_mappings.get('sku', {}).get('fields', {}).items():
                if 'table_headers' in config:
                    for header in config['table_headers']:
                        self.HEADER_MAPPINGS[header.lower()] = field

    def extract_specs(self, tables: List[Dict]) -> List[Dict]:
        """Extract SKU specifications from tables."""
        all_specs = []

        for table in tables:
            source = table.get('source', 'xml')

            # Handle kit contents (component list)
            if source == 'kit_contents':
                specs = self._parse_kit_contents(table)
                all_specs.extend(specs)
            # Handle regular spec tables
            elif self._is_spec_table(table) or source == 'story_specs':
                specs = self._parse_spec_table(table)
                all_specs.extend(specs)

        return all_specs

    def _parse_kit_contents(self, table: Dict) -> List[Dict]:
        """Parse kit contents table into SKU specs."""
        specs = []
        for row in table.get('rows', []):
            if len(row) >= 3:
                qty, desc, sku = row[0], row[1], row[2]
                specs.append({
                    'sku_code': self._clean_value(sku),
                    'model': self._clean_value(desc),
                    'quantity': qty,
                    'component_type': 'kit_component',
                })
        return specs

    def _is_spec_table(self, table: Dict) -> bool:
        """Check if table contains technical specifications."""
        headers = table.get('headers', [])
        if not headers:
            return False

        # Check for spec-related headers
        spec_indicators = [
            'caratteristiche', 'dati tecnici', 'specifications',
            'alimentazione', 'voltage', 'potenza', 'power',
            'codice', 'modello', 'code',
        ]

        header_text = ' '.join(headers).lower()
        return any(ind in header_text for ind in spec_indicators)

    def _parse_spec_table(self, table: Dict) -> List[Dict]:
        """Parse a specification table into structured data."""
        specs = []
        headers = [h.lower().strip() for h in table.get('headers', [])]

        # Map headers to standardized names
        column_mapping = {}
        for i, header in enumerate(headers):
            normalized = self._normalize_header(header)
            if normalized:
                column_mapping[i] = normalized

        # Parse each row
        for row in table.get('rows', []):
            if not any(row):  # Skip empty rows
                continue

            spec = {}
            for i, cell in enumerate(row):
                if i in column_mapping:
                    field_name = column_mapping[i]
                    spec[field_name] = self._clean_value(cell)

            # Try to extract SKU from first column if not mapped
            if 'sku_code' not in spec and len(row) > 0:
                sku = self._extract_sku(row[0])
                if sku:
                    spec['sku_code'] = sku

            if spec:  # Only add if we extracted something
                specs.append(spec)

        return specs

    def _normalize_header(self, header: str) -> Optional[str]:
        """Normalize a header to standard field name."""
        header_lower = header.lower().strip()

        # Direct mapping
        if header_lower in self.HEADER_MAPPINGS:
            return self.HEADER_MAPPINGS[header_lower]

        # Partial match
        for key, value in self.HEADER_MAPPINGS.items():
            if key in header_lower or header_lower in key:
                return value

        return None

    def _clean_value(self, value: str) -> str:
        """Clean and normalize a cell value."""
        if not value:
            return ""

        # Remove extra whitespace
        value = ' '.join(value.split())

        # Apply common corrections (only if not already correct)
        corrections = {
            'Scheda eletttronica': 'Scheda elettronica',
            'Contentore': 'Contenitore',
            'Interfaccia US': 'Interfaccia BUS',
        }

        # Fix Hz typo only if it ends with "H" but not "Hz"
        value = re.sub(r'(\d+/\d+)\s*H(?!z)', r'\1 Hz', value)

        for wrong, correct in corrections.items():
            value = value.replace(wrong, correct)

        return value

    def _extract_sku(self, text: str) -> Optional[str]:
        """Extract SKU code from text."""
        # Pattern: 6-7 digits optionally followed by letters
        match = re.search(r'\d{6,7}[A-Z]*', str(text))
        return match.group() if match else None


def extract_tables(tables: List[Dict], field_mappings: Dict = None) -> List[Dict]:
    """Convenience function to extract specifications from tables."""
    extractor = TableExtractor(field_mappings)
    return extractor.extract_specs(tables)
