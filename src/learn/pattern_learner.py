#!/usr/bin/env python3
"""
Pattern Learner - Learn extraction patterns from corrections

Analyzes corrections log and suggests updates to field mappings
and extraction rules.
"""

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class PatternLearner:
    """Learn patterns from human corrections."""

    def __init__(self, corrections_path: str, mappings_path: str = None):
        self.corrections_path = Path(corrections_path)
        self.mappings_path = Path(mappings_path) if mappings_path else None
        self.corrections: List[Dict] = []
        self.mappings: Dict = {}

    def load(self) -> None:
        """Load corrections and current mappings."""
        # Load corrections
        if self.corrections_path.exists():
            with open(self.corrections_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.corrections = data.get('corrections', [])

        # Load mappings
        if self.mappings_path and self.mappings_path.exists():
            with open(self.mappings_path, 'r', encoding='utf-8') as f:
                self.mappings = json.load(f)

    def analyze_corrections(self) -> Dict:
        """Analyze corrections to find patterns.

        Returns: Dict with suggested updates
        """
        # Group corrections by type
        typo_corrections = []
        column_mappings = []
        value_patterns = []

        for correction in self.corrections:
            extracted = correction.get('extracted', '')
            expected = correction.get('expected', '')
            field = correction.get('field', '')

            if not extracted and expected:
                # Missing extraction - suggest column mapping
                column_mappings.append({
                    'field': field,
                    'expected': expected,
                    'file': correction.get('file', ''),
                })
            elif extracted and expected and extracted != expected:
                # Check if it's a typo (similar strings)
                if self._is_typo(extracted, expected):
                    typo_corrections.append({
                        'wrong': extracted,
                        'correct': expected,
                        'field': field,
                    })
                else:
                    # Different value - analyze pattern
                    value_patterns.append({
                        'extracted': extracted,
                        'expected': expected,
                        'field': field,
                    })

        # Generate suggestions
        suggestions = {
            'typo_corrections': self._deduplicate_typos(typo_corrections),
            'column_mapping_issues': column_mappings,
            'value_pattern_issues': value_patterns,
            'summary': {
                'total_corrections': len(self.corrections),
                'typos': len(typo_corrections),
                'missing_mappings': len(column_mappings),
                'value_mismatches': len(value_patterns),
            }
        }

        return suggestions

    def _is_typo(self, s1: str, s2: str) -> bool:
        """Check if two strings differ only by a typo."""
        if not s1 or not s2:
            return False

        # Simple heuristic: if strings are similar length and differ by few chars
        len_diff = abs(len(s1) - len(s2))
        if len_diff > 3:
            return False

        # Count differing characters
        diff_count = sum(1 for a, b in zip(s1, s2) if a != b)
        diff_count += len_diff

        return diff_count <= 3

    def _deduplicate_typos(self, typos: List[Dict]) -> List[Dict]:
        """Remove duplicate typo corrections."""
        seen = set()
        unique = []

        for typo in typos:
            key = (typo['wrong'], typo['correct'])
            if key not in seen:
                seen.add(key)
                unique.append(typo)

        return unique

    def apply_to_mappings(self, suggestions: Dict) -> Dict:
        """Apply suggestions to field mappings.

        Returns: Updated mappings
        """
        if not self.mappings:
            return self.mappings

        updated = self.mappings.copy()

        # Add typo corrections
        if 'global_text_corrections' not in updated:
            updated['global_text_corrections'] = {}

        for typo in suggestions.get('typo_corrections', []):
            wrong = typo['wrong']
            correct = typo['correct']
            updated['global_text_corrections'][wrong] = correct

        return updated

    def save_updated_mappings(self, updated: Dict) -> None:
        """Save updated mappings to file."""
        if self.mappings_path:
            # Add metadata
            updated['last_updated'] = datetime.now().strftime('%Y-%m-%d')

            with open(self.mappings_path, 'w', encoding='utf-8') as f:
                json.dump(updated, f, indent=2, ensure_ascii=False)


def learn_patterns(corrections_path: str, mappings_path: str = None) -> Dict:
    """Analyze corrections and suggest pattern updates."""
    learner = PatternLearner(corrections_path, mappings_path)
    learner.load()
    return learner.analyze_corrections()


def main():
    parser = argparse.ArgumentParser(description='Learn patterns from corrections')
    parser.add_argument('--corrections', '-c', required=True,
                        help='Path to corrections_log.json')
    parser.add_argument('--mappings', '-m',
                        help='Path to field_mappings.json to update')
    parser.add_argument('--apply', '-a', action='store_true',
                        help='Apply suggestions to mappings file')

    args = parser.parse_args()

    learner = PatternLearner(args.corrections, args.mappings)
    learner.load()

    suggestions = learner.analyze_corrections()

    # Print summary
    print("\n=== Pattern Analysis ===")
    print(f"Total corrections analyzed: {suggestions['summary']['total_corrections']}")
    print(f"Typo corrections found: {suggestions['summary']['typos']}")
    print(f"Missing column mappings: {suggestions['summary']['missing_mappings']}")
    print(f"Value pattern issues: {suggestions['summary']['value_mismatches']}")

    if suggestions['typo_corrections']:
        print("\n=== Suggested Typo Corrections ===")
        for typo in suggestions['typo_corrections']:
            print(f"  '{typo['wrong']}' → '{typo['correct']}'")

    if suggestions['column_mapping_issues']:
        print("\n=== Column Mapping Issues ===")
        for issue in suggestions['column_mapping_issues'][:10]:
            print(f"  Field '{issue['field']}' missing in {issue['file']}")

    # Apply if requested
    if args.apply and args.mappings:
        updated = learner.apply_to_mappings(suggestions)
        learner.save_updated_mappings(updated)
        print(f"\nUpdated mappings saved to: {args.mappings}")

    # Output as JSON
    print("\n" + json.dumps(suggestions, indent=2))


if __name__ == '__main__':
    main()
