"""
IDML Parser - Extracts content from InDesign IDML files

IDML files are ZIP archives containing XML files:
- designmap.xml - Main structure
- Spreads/Spread_*.xml - Page content
- Stories/Story_*.xml - Text content
- Resources/Styles.xml - Style definitions
"""

import zipfile
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from lxml import etree
import re


class IDMLParser:
    """Parse IDML files and extract structured content."""

    # IDML namespace
    NAMESPACES = {
        'idPkg': 'http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging',
    }

    def __init__(self, idml_path: str):
        self.idml_path = Path(idml_path)
        self.filename = self.idml_path.stem
        self.content: Dict = {}
        self.stories: Dict[str, etree._Element] = {}
        self.spreads: List[etree._Element] = []
        self.styles: Dict[str, Dict] = {}

    def parse(self) -> Dict:
        """Extract all content from IDML file."""
        if not self.idml_path.exists():
            raise FileNotFoundError(f"IDML file not found: {self.idml_path}")

        with zipfile.ZipFile(self.idml_path, 'r') as zf:
            # Load all XML files
            self._load_designmap(zf)
            self._load_stories(zf)
            self._load_spreads(zf)
            self._load_styles(zf)

        # Extract structured content
        self.content = {
            'filename': self.filename,
            'pages': self._extract_pages(),
            'category': self._extract_category(),
            'product_name': self._extract_product_name(),
            'description': self._extract_description(),
            'tables': self._extract_tables(),
            'accessories': self._extract_accessories(),
            'images': self._extract_images(),
        }

        return self.content

    def _load_designmap(self, zf: zipfile.ZipFile) -> None:
        """Load main designmap.xml."""
        try:
            with zf.open('designmap.xml') as f:
                self.designmap = etree.parse(f)
        except KeyError:
            self.designmap = None

    def _load_stories(self, zf: zipfile.ZipFile) -> None:
        """Load all story XML files."""
        for name in zf.namelist():
            if name.startswith('Stories/') and name.endswith('.xml'):
                with zf.open(name) as f:
                    tree = etree.parse(f)
                    story_id = Path(name).stem
                    self.stories[story_id] = tree.getroot()

    def _load_spreads(self, zf: zipfile.ZipFile) -> None:
        """Load all spread XML files."""
        for name in zf.namelist():
            if name.startswith('Spreads/') and name.endswith('.xml'):
                with zf.open(name) as f:
                    tree = etree.parse(f)
                    self.spreads.append(tree.getroot())

    def _load_styles(self, zf: zipfile.ZipFile) -> None:
        """Load style definitions."""
        try:
            with zf.open('Resources/Styles.xml') as f:
                tree = etree.parse(f)
                root = tree.getroot()

                # Extract paragraph styles
                for style in root.iter('ParagraphStyle'):
                    name = style.get('Name', '')
                    self.styles[name] = {
                        'type': 'paragraph',
                        'self': style.get('Self', ''),
                    }

                # Extract character styles
                for style in root.iter('CharacterStyle'):
                    name = style.get('Name', '')
                    self.styles[name] = {
                        'type': 'character',
                        'self': style.get('Self', ''),
                    }
        except KeyError:
            pass

    def _extract_pages(self) -> str:
        """Extract page numbers from filename or metadata."""
        # Pattern: Pages_XXX-YYY_Name.idml
        match = re.search(r'Pages?[_\s]*(\d+[-–]\d+)', self.filename, re.IGNORECASE)
        if match:
            return match.group(1).replace('–', '-')

        # Try from filename directly
        match = re.search(r'(\d+[-–]\d+)', self.filename)
        if match:
            return match.group(1).replace('–', '-')

        return ""

    def _extract_category(self) -> str:
        """Extract product category from styled text."""
        category_patterns = [
            'AUTOMAZIONI PER CANCELLI',
            'BARRIERE STRADALI',
            'BARRIERE AUTOMATICHE',
            'AUTOMAZIONI PER PORTE',
        ]

        for story in self.stories.values():
            text = self._get_story_text(story)
            for pattern in category_patterns:
                if pattern in text.upper():
                    return pattern.title()

        # Try finding by style
        for story in self.stories.values():
            for elem in story.iter():
                style = elem.get('AppliedParagraphStyle', '') + elem.get('AppliedCharacterStyle', '')
                if 'categoria' in style.lower() or 'category' in style.lower():
                    content = self._get_element_text(elem)
                    if content:
                        return content.strip()

        return ""

    def _extract_product_name(self) -> str:
        """Extract main product name/title."""
        for story in self.stories.values():
            for elem in story.iter():
                style = elem.get('AppliedParagraphStyle', '')
                if 'titolo' in style.lower() or 'title' in style.lower():
                    content = self._get_element_text(elem)
                    if content:
                        return content.strip()

        # Fallback: extract from filename
        # Pattern: Pages_XXX-YYY_ProductName.idml
        parts = self.filename.replace('Pages_', '').split('_')
        if len(parts) > 1:
            return parts[-1]

        return self.filename

    def _extract_description(self) -> str:
        """Extract product description."""
        for story in self.stories.values():
            for elem in story.iter():
                style = elem.get('AppliedParagraphStyle', '')
                if 'descrizione' in style.lower() or 'description' in style.lower():
                    content = self._get_element_text(elem)
                    if content:
                        return content.strip()[:500]  # Max 500 chars
        return ""

    def _extract_tables(self) -> List[Dict]:
        """Extract all tables from spreads and stories."""
        tables = []

        # Check for XML Table elements in spreads
        for spread in self.spreads:
            for table in spread.iter('Table'):
                table_data = self._parse_table(table)
                if table_data:
                    tables.append(table_data)

        # Check for XML Table elements in stories
        for story in self.stories.values():
            for table in story.iter('Table'):
                table_data = self._parse_table(table)
                if table_data:
                    tables.append(table_data)

        # Also extract spec-like content from Stories (vertical tables in text)
        spec_table = self._extract_specs_from_stories()
        if spec_table:
            tables.append(spec_table)

        return tables

    def _extract_specs_from_stories(self) -> Optional[Dict]:
        """Extract technical specifications from story text content.

        Many IDML files store specs as sequential text elements:
        Header1, Value1, Header2, Value2, etc.
        """
        spec_keywords = [
            'Tensione di alimentazione', 'Alimentazione', 'Potenza max',
            'Motore elettrico', 'Peso', 'Grado di protezione', 'Temperatura',
            'Frequenza di utilizzo', 'Dimensioni', 'Coppia max'
        ]

        for story in self.stories.values():
            contents = [c.text.strip() for c in story.iter('Content')
                       if c.text and c.text.strip()]

            # Check if this story contains spec data
            full_text = ' '.join(contents)
            if not any(kw in full_text for kw in spec_keywords):
                continue

            # Parse header/value pairs
            # Format: Modello, val1, val2, Header1, val1, val2, Header2, ...
            headers = []
            rows = []
            models = []

            i = 0
            while i < len(contents):
                text = contents[i]

                # Check if this is a header (spec name)
                if text == 'Modello':
                    # Next items are model names
                    i += 1
                    while i < len(contents) and not self._is_spec_header(contents[i]):
                        models.append(contents[i])
                        i += 1
                    continue

                if self._is_spec_header(text):
                    headers.append(text)
                    # Collect values for this header
                    values = []
                    i += 1
                    while i < len(contents) and not self._is_spec_header(contents[i]):
                        values.append(contents[i])
                        i += 1

                    # Add to rows (pad if needed)
                    while len(rows) < len(values):
                        rows.append({})
                    for j, val in enumerate(values):
                        rows[j][headers[-1]] = val
                else:
                    i += 1

            if headers and rows:
                # Add model names to rows
                for j, model in enumerate(models):
                    if j < len(rows):
                        rows[j]['Modello'] = model

                return {
                    'headers': ['Modello'] + headers if models else headers,
                    'rows': [[r.get(h, '') for h in (['Modello'] + headers if models else headers)]
                            for r in rows],
                    'column_count': len(headers) + (1 if models else 0),
                    'source': 'story_specs'
                }

        return None

    def _is_spec_header(self, text: str) -> bool:
        """Check if text looks like a specification header."""
        spec_headers = [
            'tensione', 'alimentazione', 'potenza', 'motore', 'peso',
            'grado di protezione', 'temperatura', 'frequenza', 'dimensioni',
            'coppia', 'forza', 'velocità', 'lunghezza', 'spazio', 'pignone',
            'condensatore', 'termoprotezione', 'encoder', 'tipo', 'corsa',
            'angolo', 'staffe', 'apparecchiatura', 'larghezza', 'portata'
        ]
        text_lower = text.lower()
        return any(h in text_lower for h in spec_headers)

    def _parse_table(self, table_elem: etree._Element) -> Optional[Dict]:
        """Parse a single table element."""
        rows = []
        headers = []

        # Get table dimensions
        body_row_count = int(table_elem.get('BodyRowCount', 0))
        header_row_count = int(table_elem.get('HeaderRowCount', 0))
        column_count = int(table_elem.get('ColumnCount', 0))

        if column_count == 0:
            return None

        # Extract cells
        cells = list(table_elem.iter('Cell'))

        current_row = []
        for i, cell in enumerate(cells):
            cell_content = self._get_element_text(cell)
            current_row.append(cell_content.strip() if cell_content else "")

            if len(current_row) == column_count:
                if len(rows) < header_row_count:
                    headers.append(current_row)
                else:
                    rows.append(current_row)
                current_row = []

        return {
            'headers': headers[0] if headers else [],
            'rows': rows,
            'column_count': column_count,
        }

    def _extract_accessories(self) -> List[Dict]:
        """Extract accessory list items."""
        accessories = []
        sku_pattern = re.compile(r'\d{6,7}[A-Z]*')

        in_accessory_section = False

        for story in self.stories.values():
            text = self._get_story_text(story)

            # Check if this contains accessory section
            if any(marker in text for marker in ['Accessori', 'Optional', 'Ricambi']):
                in_accessory_section = True

            if in_accessory_section:
                # Find SKU codes with their descriptions
                lines = text.split('\n')
                for line in lines:
                    match = sku_pattern.search(line)
                    if match:
                        sku = match.group()
                        name = line.replace(sku, '').strip(' \t-–•')
                        if name:
                            accessories.append({
                                'name': name,
                                'sku': sku,
                            })

        return accessories

    def _extract_images(self) -> List[str]:
        """Extract image references."""
        images = []

        for spread in self.spreads:
            for img in spread.iter('Image'):
                href = img.get('href', '')
                if href:
                    images.append(href)

            for link in spread.iter('Link'):
                href = link.get('LinkResourceURI', '')
                if href:
                    images.append(href)

        return images

    def _get_story_text(self, story: etree._Element) -> str:
        """Get all text content from a story."""
        texts = []
        for content in story.iter('Content'):
            if content.text:
                texts.append(content.text)
        return ' '.join(texts)

    def _get_element_text(self, elem: etree._Element) -> str:
        """Get text content from an element and its children."""
        texts = []
        for content in elem.iter('Content'):
            if content.text:
                texts.append(content.text)
        if not texts:
            # Try direct text
            if elem.text:
                texts.append(elem.text)
        return ' '.join(texts)


def parse_idml(idml_path: str) -> Dict:
    """Convenience function to parse an IDML file."""
    parser = IDMLParser(idml_path)
    return parser.parse()
