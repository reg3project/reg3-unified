"""
XLSX Writer - Writes extracted data to Excel spreadsheets

Creates XLSX files with 'prodotti' and 'sku' sheets matching
the expected reference format.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter


class XLSXWriter:
    """Write extracted data to XLSX format."""

    # Column definitions for prodotti sheet
    PRODOTTI_COLUMNS = [
        'category', 'name', 'model', 'subtitle', 'page', 'description',
        'badges', 'certifications', 'image_refs',
    ]

    # Column definitions for SKU sheet
    SKU_COLUMNS = [
        'sku_code', 'model', 'voltage', 'motor_type', 'power', 'torque',
        'weight', 'dimensions', 'ip_rating', 'temperature',
        'cycles_hour', 'cycles_day', 'speed', 'max_stroke',
        'capacitor_run', 'capacitor_start', 'limit_switch', 'release',
        'control_unit',
    ]

    def __init__(self):
        self.workbook = Workbook()

    def create_workbook(self, content: Dict, specs: List[Dict]) -> Workbook:
        """Create a workbook with prodotti and sku sheets."""
        # Remove default sheet
        if 'Sheet' in self.workbook.sheetnames:
            del self.workbook['Sheet']

        # Create sheets
        self._create_prodotti_sheet(content)
        self._create_sku_sheet(specs, content)

        return self.workbook

    def _create_prodotti_sheet(self, content: Dict) -> None:
        """Create the prodotti (products) sheet."""
        ws = self.workbook.create_sheet('prodotti')

        # Write headers
        for col, header in enumerate(self.PRODOTTI_COLUMNS, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color='DDEEFF', end_color='DDEEFF', fill_type='solid')

        # Write data row
        row_data = {
            'category': content.get('category', ''),
            'name': content.get('product_name', ''),
            'model': content.get('model', ''),
            'subtitle': content.get('subtitle', ''),
            'page': content.get('pages', ''),
            'description': content.get('description', ''),
            'badges': ', '.join(content.get('badges', [])),
            'certifications': ', '.join(content.get('certifications', [])) if content.get('certifications') else '',
            'image_refs': ', '.join(content.get('images', [])[:5]) if content.get('images') else '',
        }

        for col, header in enumerate(self.PRODOTTI_COLUMNS, 1):
            ws.cell(row=2, column=col, value=row_data.get(header, ''))

        # Adjust column widths
        self._auto_adjust_columns(ws)

    def _create_sku_sheet(self, specs: List[Dict], content: Dict) -> None:
        """Create the SKU specifications sheet."""
        ws = self.workbook.create_sheet('sku')

        # Write headers
        for col, header in enumerate(self.SKU_COLUMNS, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color='DDEEFF', end_color='DDEEFF', fill_type='solid')

        # Write data rows
        row_num = 2
        for spec in specs:
            # Add model from content if not in spec
            if 'model' not in spec:
                spec['model'] = content.get('model', '')

            for col, header in enumerate(self.SKU_COLUMNS, 1):
                value = spec.get(header, '')
                ws.cell(row=row_num, column=col, value=value)
            row_num += 1

        # If no specs, write at least one row with model
        if not specs:
            ws.cell(row=2, column=2, value=content.get('model', ''))

        # Adjust column widths
        self._auto_adjust_columns(ws)

    def _auto_adjust_columns(self, ws) -> None:
        """Auto-adjust column widths based on content."""
        for column in ws.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)

            for cell in column:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass

            # Set width with some padding
            adjusted_width = min(max_length + 2, 50)  # Max 50 chars wide
            ws.column_dimensions[column_letter].width = adjusted_width

    def save(self, output_path: str) -> None:
        """Save the workbook to file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.workbook.save(output_path)


def write_xlsx(content: Dict, specs: List[Dict], output_path: str) -> str:
    """Write extracted data to XLSX file.

    Returns: Path to created file
    """
    writer = XLSXWriter()
    writer.create_workbook(content, specs)
    writer.save(output_path)
    return output_path
