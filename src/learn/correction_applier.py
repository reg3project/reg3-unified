#!/usr/bin/env python3
"""
Correction Applier - Apply human corrections to knowledge base

Reads corrections_log.json and updates field_mappings.json with
learned patterns and fixes.
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class CorrectionApplier:
    """Apply corrections from log to knowledge base."""

    def __init__(self, corrections_path: str, mappings_path: str):
        self.corrections_path = Path(corrections_path)
        self.mappings_path = Path(mappings_path)
        self.corrections_data: Dict = {}
        self.mappings: Dict = {}

    def load(self) -> None:
        """Load corrections and mappings files."""
        # Load corrections
        if self.corrections_path.exists():
            with open(self.corrections_path, 'r', encoding='utf-8') as f:
                self.corrections_data = json.load(f)

        # Load mappings
        if self.mappings_path.exists():
            with open(self.mappings_path, 'r', encoding='utf-8') as f:
                self.mappings = json.load(f)

    def get_pending_corrections(self) -> List[Dict]:
        """Get corrections that haven't been applied yet."""
        corrections = self.corrections_data.get('corrections', [])
        return [c for c in corrections if not c.get('applied', False)]

    def apply_corrections(self) -> Dict:
        """Apply all pending corrections.

        Returns: Summary of applied corrections
        """
        pending = self.get_pending_corrections()
        if not pending:
            return {'applied': 0, 'skipped': 0}

        applied = 0
        skipped = 0

        for correction in pending:
            if self._apply_single_correction(correction):
                correction['applied'] = True
                correction['applied_date'] = datetime.now().strftime('%Y-%m-%d')
                applied += 1
            else:
                skipped += 1

        # Update metadata
        self.mappings['last_updated'] = datetime.now().strftime('%Y-%m-%d')

        return {
            'applied': applied,
            'skipped': skipped,
            'total_pending': len(pending),
        }

    def _apply_single_correction(self, correction: Dict) -> bool:
        """Apply a single correction to mappings.

        Returns: True if successfully applied
        """
        extracted = correction.get('extracted', '')
        expected = correction.get('expected', '')
        rule_update = correction.get('rule_update', '')

        # Type 1: Typo correction (extracted != expected, both non-empty)
        if extracted and expected and extracted != expected:
            return self._add_typo_correction(extracted, expected)

        # Type 2: Column mapping (extracted empty, expected has value)
        if not extracted and expected:
            # Log for manual review - can't auto-apply
            return False

        # Type 3: Rule-based update
        if rule_update:
            # Parse rule update text for instructions
            return self._apply_rule_update(rule_update, correction)

        return False

    def _add_typo_correction(self, wrong: str, correct: str) -> bool:
        """Add a typo correction to global corrections."""
        if 'global_text_corrections' not in self.mappings:
            self.mappings['global_text_corrections'] = {}

        # Only add if not already present
        if wrong not in self.mappings['global_text_corrections']:
            self.mappings['global_text_corrections'][wrong] = correct
            return True

        return self.mappings['global_text_corrections'][wrong] == correct

    def _apply_rule_update(self, rule_text: str, correction: Dict) -> bool:
        """Parse and apply a rule update instruction.

        Returns: True if successfully applied
        """
        rule_lower = rule_text.lower()

        # Typo correction rule
        if 'typo correction' in rule_lower or 'typo fix' in rule_lower:
            extracted = correction.get('extracted', '')
            expected = correction.get('expected', '')
            if extracted and expected:
                return self._add_typo_correction(extracted, expected)

        # Column mapping rule
        if 'add column' in rule_lower or 'column mapping' in rule_lower:
            # Would need more context to auto-apply
            # Mark as needing manual review
            return False

        # Header pattern rule
        if 'header' in rule_lower or 'pattern' in rule_lower:
            # Would need specific header info to apply
            return False

        return False

    def save(self) -> None:
        """Save updated files."""
        # Save corrections (with applied flags)
        with open(self.corrections_path, 'w', encoding='utf-8') as f:
            json.dump(self.corrections_data, f, indent=2, ensure_ascii=False)

        # Save mappings
        with open(self.mappings_path, 'w', encoding='utf-8') as f:
            json.dump(self.mappings, f, indent=2, ensure_ascii=False)


def apply_corrections(corrections_path: str, mappings_path: str) -> Dict:
    """Apply corrections from log to mappings."""
    applier = CorrectionApplier(corrections_path, mappings_path)
    applier.load()
    result = applier.apply_corrections()
    applier.save()
    return result


def main():
    parser = argparse.ArgumentParser(description='Apply corrections to knowledge base')
    parser.add_argument('--corrections', '-c', required=True,
                        help='Path to corrections_log.json')
    parser.add_argument('--mappings', '-m', required=True,
                        help='Path to field_mappings.json')
    parser.add_argument('--dry-run', '-d', action='store_true',
                        help='Show what would be applied without saving')

    args = parser.parse_args()

    applier = CorrectionApplier(args.corrections, args.mappings)
    applier.load()

    pending = applier.get_pending_corrections()
    print(f"Found {len(pending)} pending corrections")

    if args.dry_run:
        print("\n=== Dry Run - Would Apply: ===")
        for c in pending:
            print(f"  {c.get('file', '?')}: {c.get('field', '?')}")
            print(f"    Extracted: {c.get('extracted', '')}")
            print(f"    Expected:  {c.get('expected', '')}")
            print(f"    Rule: {c.get('rule_update', 'N/A')}")
            print()
    else:
        result = applier.apply_corrections()
        applier.save()

        print(f"\n=== Results ===")
        print(f"Applied: {result['applied']}")
        print(f"Skipped: {result['skipped']}")
        print(f"\nUpdated files:")
        print(f"  - {args.corrections}")
        print(f"  - {args.mappings}")


if __name__ == '__main__':
    main()
