"""
Comparator - Compare extracted XLSX against reference

Performs cell-by-cell comparison and calculates accuracy metrics.
"""

from typing import Dict, List, Optional, Tuple
import pandas as pd
from dataclasses import dataclass, field
from enum import Enum


class CompareStatus(Enum):
    MATCH = "match"
    MISMATCH = "mismatch"
    NEW = "new"  # In extracted but not in reference
    MISSING = "missing"  # In reference but not in extracted
    EMPTY_BOTH = "empty_both"


@dataclass
class CellComparison:
    """Result of comparing a single cell."""
    sheet: str
    row: int
    column: str
    extracted: str
    expected: str
    status: CompareStatus

    def to_dict(self) -> Dict:
        return {
            'sheet': self.sheet,
            'row': self.row,
            'column': self.column,
            'extracted': self.extracted,
            'expected': self.expected,
            'status': self.status.value,
        }


@dataclass
class SheetComparison:
    """Result of comparing a sheet."""
    name: str
    matches: int = 0
    mismatches: int = 0
    new_fields: int = 0
    missing_fields: int = 0
    empty_both: int = 0
    details: List[CellComparison] = field(default_factory=list)

    @property
    def total(self) -> int:
        return self.matches + self.mismatches + self.new_fields + self.missing_fields

    @property
    def accuracy(self) -> float:
        if self.total == 0:
            return 100.0
        comparable = self.matches + self.mismatches
        if comparable == 0:
            return 100.0
        return (self.matches / comparable) * 100


@dataclass
class FileComparison:
    """Result of comparing a file."""
    filename: str
    sheets: Dict[str, SheetComparison] = field(default_factory=dict)

    @property
    def total_matches(self) -> int:
        return sum(s.matches for s in self.sheets.values())

    @property
    def total_mismatches(self) -> int:
        return sum(s.mismatches for s in self.sheets.values())

    @property
    def total_new(self) -> int:
        return sum(s.new_fields for s in self.sheets.values())

    @property
    def total_missing(self) -> int:
        return sum(s.missing_fields for s in self.sheets.values())

    @property
    def accuracy(self) -> float:
        total = self.total_matches + self.total_mismatches
        if total == 0:
            return 100.0
        return (self.total_matches / total) * 100

    def to_dict(self) -> Dict:
        return {
            'file': self.filename,
            'accuracy': round(self.accuracy, 2),
            'matches': self.total_matches,
            'mismatches': self.total_mismatches,
            'new_fields': self.total_new,
            'missing_fields': self.total_missing,
            'sheets': {
                name: {
                    'accuracy': round(sheet.accuracy, 2),
                    'matches': sheet.matches,
                    'mismatches': sheet.mismatches,
                    'new_fields': sheet.new_fields,
                    'missing_fields': sheet.missing_fields,
                }
                for name, sheet in self.sheets.items()
            },
            'details': [
                detail.to_dict()
                for sheet in self.sheets.values()
                for detail in sheet.details
                if detail.status != CompareStatus.MATCH
            ]
        }


class Comparator:
    """Compare extracted XLSX against reference."""

    def __init__(self, fuzzy_match: bool = False):
        """Initialize comparator.

        Args:
            fuzzy_match: If True, perform fuzzy string matching
        """
        self.fuzzy_match = fuzzy_match

    def compare(
        self,
        extracted: Dict[str, pd.DataFrame],
        reference: Dict[str, pd.DataFrame],
        filename: str = ""
    ) -> FileComparison:
        """Compare extracted sheets against reference.

        Returns: FileComparison with detailed results
        """
        result = FileComparison(filename=filename)

        # Compare each sheet
        all_sheets = set(extracted.keys()) | set(reference.keys())

        for sheet_name in all_sheets:
            ext_sheet = extracted.get(sheet_name.lower()) or extracted.get(sheet_name)
            ref_sheet = reference.get(sheet_name.lower()) or reference.get(sheet_name)

            sheet_result = self._compare_sheets(
                ext_sheet,
                ref_sheet,
                sheet_name
            )
            result.sheets[sheet_name] = sheet_result

        return result

    def _compare_sheets(
        self,
        extracted: Optional[pd.DataFrame],
        reference: Optional[pd.DataFrame],
        sheet_name: str
    ) -> SheetComparison:
        """Compare two sheets."""
        result = SheetComparison(name=sheet_name)

        # Handle missing sheets
        if extracted is None and reference is None:
            return result

        if extracted is None:
            # All reference fields are missing
            if reference is not None:
                result.missing_fields = reference.size
            return result

        if reference is None:
            # All extracted fields are new
            result.new_fields = extracted.size
            return result

        # Get all columns
        all_columns = set(extracted.columns) | set(reference.columns)

        # Get max rows
        max_rows = max(len(extracted), len(reference))

        # Compare cell by cell
        for col in all_columns:
            ext_has_col = col in extracted.columns
            ref_has_col = col in reference.columns

            for row in range(max_rows):
                ext_value = ""
                ref_value = ""

                if ext_has_col and row < len(extracted):
                    ext_value = str(extracted.iloc[row][col]).strip()
                if ref_has_col and row < len(reference):
                    ref_value = str(reference.iloc[row][col]).strip()

                # Normalize empty values
                if ext_value in ('nan', 'None', ''):
                    ext_value = ''
                if ref_value in ('nan', 'None', ''):
                    ref_value = ''

                # Determine status
                status = self._compare_values(ext_value, ref_value, ext_has_col, ref_has_col)

                # Update counts
                if status == CompareStatus.MATCH:
                    result.matches += 1
                elif status == CompareStatus.MISMATCH:
                    result.mismatches += 1
                    result.details.append(CellComparison(
                        sheet=sheet_name,
                        row=row,
                        column=col,
                        extracted=ext_value,
                        expected=ref_value,
                        status=status
                    ))
                elif status == CompareStatus.NEW:
                    result.new_fields += 1
                    result.details.append(CellComparison(
                        sheet=sheet_name,
                        row=row,
                        column=col,
                        extracted=ext_value,
                        expected=ref_value,
                        status=status
                    ))
                elif status == CompareStatus.MISSING:
                    result.missing_fields += 1
                    result.details.append(CellComparison(
                        sheet=sheet_name,
                        row=row,
                        column=col,
                        extracted=ext_value,
                        expected=ref_value,
                        status=status
                    ))
                else:
                    result.empty_both += 1

        return result

    def _compare_values(
        self,
        extracted: str,
        reference: str,
        ext_has_col: bool,
        ref_has_col: bool
    ) -> CompareStatus:
        """Compare two values and determine status."""

        # Both empty
        if not extracted and not reference:
            return CompareStatus.EMPTY_BOTH

        # Column exists only in extracted
        if ext_has_col and not ref_has_col:
            if extracted:
                return CompareStatus.NEW
            return CompareStatus.EMPTY_BOTH

        # Column exists only in reference
        if ref_has_col and not ext_has_col:
            if reference:
                return CompareStatus.MISSING
            return CompareStatus.EMPTY_BOTH

        # Both have value - compare
        if extracted == reference:
            return CompareStatus.MATCH

        # Try normalized comparison
        if self._normalize_value(extracted) == self._normalize_value(reference):
            return CompareStatus.MATCH

        # One empty, one not
        if extracted and not reference:
            return CompareStatus.NEW
        if reference and not extracted:
            return CompareStatus.MISSING

        # Both have different values
        return CompareStatus.MISMATCH

    def _normalize_value(self, value: str) -> str:
        """Normalize value for comparison."""
        if not value:
            return ""

        # Lowercase
        value = value.lower()

        # Remove extra whitespace
        value = ' '.join(value.split())

        # Common normalizations
        value = value.replace('–', '-')
        value = value.replace('—', '-')
        value = value.replace('  ', ' ')

        return value


def compare_files(
    extracted: Dict[str, pd.DataFrame],
    reference: Dict[str, pd.DataFrame],
    filename: str = ""
) -> FileComparison:
    """Compare extracted sheets against reference."""
    comparator = Comparator()
    return comparator.compare(extracted, reference, filename)
