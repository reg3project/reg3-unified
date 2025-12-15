"""
Text Extractor - Extracts and processes text content from IDML

Handles styled text extraction, pattern matching, and text cleanup.
"""

import re
from typing import Dict, List, Optional, Tuple


class TextExtractor:
    """Extract and process text content from IDML data."""

    # Category normalization
    CATEGORY_NORMALIZATION = {
        'AUTOMAZIONI PER CANCELLI SCORREVOLI': 'Cancelli Scorrevoli',
        'AUTOMAZIONI PER CANCELLI A BATTENTE': 'Cancelli a Battente',
        'BARRIERE STRADALI': 'Barriere',
        'BARRIERE AUTOMATICHE': 'Barriere',
        'AUTOMAZIONI PER PORTE SEZIONALI': 'Porte Sezionali',
        'AUTOMAZIONI PER PORTE BASCULANTI': 'Porte Basculanti',
    }

    def __init__(self, corrections: Dict = None):
        """Initialize with optional text corrections."""
        self.corrections = corrections or {}

    def normalize_category(self, category: str) -> str:
        """Normalize category name."""
        category_upper = category.upper().strip()

        for raw, normalized in self.CATEGORY_NORMALIZATION.items():
            if raw in category_upper:
                return normalized

        return category.title()

    def extract_model_name(self, text: str) -> Tuple[str, str]:
        """Extract model number and subtitle from product name.

        Returns: (model, subtitle)
        """
        if not text:
            return "", ""

        # Pattern: "MODEL – Description" or "MODEL - Description"
        match = re.match(r'^([A-Z0-9]+(?:\s+[A-Za-z]+)?)\s*[–-]\s*(.*)$', text.strip())
        if match:
            return match.group(1).strip(), match.group(2).strip()

        # Just model number
        match = re.match(r'^([A-Z0-9]+(?:\s+[A-Za-z]+)?)', text.strip())
        if match:
            return match.group(1).strip(), ""

        return text.strip(), ""

    def clean_text(self, text: str) -> str:
        """Apply text corrections and cleanup."""
        if not text:
            return ""

        # Remove excessive whitespace
        text = ' '.join(text.split())

        # Apply corrections from knowledge base
        for wrong, correct in self.corrections.items():
            text = text.replace(wrong, correct)

        return text.strip()

    def extract_badges(self, content: Dict) -> List[str]:
        """Extract product badges/certifications from images and text."""
        badges = []

        # Check image references for certifications
        for img in content.get('images', []):
            if 'CE' in img.upper():
                badges.append('CE')
            if 'UL' in img.upper():
                badges.append('UL')
            if 'IP' in img.upper():
                match = re.search(r'IP\d{2}', img.upper())
                if match:
                    badges.append(match.group())

        return list(set(badges))  # Remove duplicates

    def validate_voltage(self, voltage: str) -> bool:
        """Validate voltage format."""
        if not voltage:
            return False
        # Must contain V and either Hz or ~
        return 'V' in voltage and ('Hz' in voltage or '~' in voltage)

    def validate_power(self, power: str) -> bool:
        """Validate power format."""
        if not power:
            return False
        return bool(re.search(r'\d+(?:\.\d+)?\s*(?:W|kW)', power, re.IGNORECASE))

    def validate_weight(self, weight: str) -> bool:
        """Validate weight format."""
        if not weight:
            return False
        return bool(re.search(r'\d+(?:\.\d+)?\s*(?:kg|g)', weight, re.IGNORECASE))

    def validate_temperature(self, temp: str) -> bool:
        """Validate temperature range format."""
        if not temp:
            return False
        return '°C' in temp

    def validate_ip_rating(self, ip: str) -> bool:
        """Validate IP rating format."""
        if not ip:
            return False
        return bool(re.match(r'^IP\d{2}', ip.upper()))


def extract_text(content: Dict, corrections: Dict = None) -> Dict:
    """Process and clean text content from IDML."""
    extractor = TextExtractor(corrections)

    # Normalize category
    if content.get('category'):
        content['category'] = extractor.normalize_category(content['category'])

    # Extract model and subtitle
    if content.get('product_name'):
        model, subtitle = extractor.extract_model_name(content['product_name'])
        content['model'] = model
        content['subtitle'] = subtitle

    # Clean description
    if content.get('description'):
        content['description'] = extractor.clean_text(content['description'])

    # Extract badges
    content['badges'] = extractor.extract_badges(content)

    return content
