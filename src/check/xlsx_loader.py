"""
XLSX Loader - Load and normalize Excel spreadsheets for comparison

Handles loading both extracted and reference XLSX files,
normalizing data for accurate comparison.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
from openpyxl import load_workbook


class XLSXLoader:
    """Load and normalize XLSX files."""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.sheets: Dict[str, pd.DataFrame] = {}

    def load(self) -> Dict[str, pd.DataFrame]:
        """Load all sheets from XLSX file."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        # Load each sheet
        xlsx = pd.ExcelFile(self.file_path)
        for sheet_name in xlsx.sheet_names:
            df = pd.read_excel(xlsx, sheet_name=sheet_name)
            self.sheets[sheet_name] = self._normalize_dataframe(df)

        return self.sheets

    def _normalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize dataframe for comparison."""
        # Convert all values to strings and strip whitespace
        df = df.fillna('')
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            # Replace 'nan' strings with empty
            df[col] = df[col].replace('nan', '')

        # Normalize column names (lowercase, strip)
        df.columns = [str(c).lower().strip() for c in df.columns]

        return df

    def get_sheet(self, sheet_name: str) -> Optional[pd.DataFrame]:
        """Get a specific sheet by name."""
        return self.sheets.get(sheet_name.lower()) or self.sheets.get(sheet_name)

    def get_cell(self, sheet_name: str, row: int, col: str) -> str:
        """Get a specific cell value."""
        sheet = self.get_sheet(sheet_name)
        if sheet is None or row >= len(sheet):
            return ""

        col = col.lower()
        if col not in sheet.columns:
            return ""

        return str(sheet.iloc[row][col])


def load_xlsx(file_path: str) -> Dict[str, pd.DataFrame]:
    """Load XLSX file and return normalized sheets."""
    loader = XLSXLoader(file_path)
    return loader.load()


def load_xlsx_pair(extracted_path: str, reference_path: str) -> Tuple[Dict, Dict]:
    """Load both extracted and reference XLSX files."""
    extracted = load_xlsx(extracted_path)
    reference = load_xlsx(reference_path)
    return extracted, reference
