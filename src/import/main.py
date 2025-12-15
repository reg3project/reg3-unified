#!/usr/bin/env python3
"""
REG3 Import - IDML to XLSX Extraction Pipeline

Usage:
    python main.py --input input/idml/learning --output output/xlsx/learning
    python main.py --file input/idml/learning/B614.idml --output output/xlsx/
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional

from idml_parser import IDMLParser, parse_idml
from table_extractor import TableExtractor, extract_tables
from text_extractor import TextExtractor, extract_text
from xlsx_writer import XLSXWriter, write_xlsx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_field_mappings(mappings_path: str) -> Dict:
    """Load field mappings from JSON file."""
    if not mappings_path or not Path(mappings_path).exists():
        return {}

    with open(mappings_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_corrections(knowledge_dir: str) -> Dict:
    """Load text corrections from knowledge base."""
    corrections = {}

    # Load from field_mappings
    mappings_path = Path(knowledge_dir) / 'field_mappings.json'
    if mappings_path.exists():
        with open(mappings_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            corrections.update(data.get('global_text_corrections', {}))

    return corrections


def process_idml(idml_path: str, output_dir: str, field_mappings: Dict = None, corrections: Dict = None) -> Optional[str]:
    """Process a single IDML file and generate XLSX.

    Returns: Path to output file or None on error
    """
    idml_path = Path(idml_path)
    logger.info(f"Processing: {idml_path.name}")

    try:
        # Step 1: Parse IDML
        parser = IDMLParser(str(idml_path))
        content = parser.parse()
        logger.debug(f"  Parsed: {len(content.get('tables', []))} tables, {len(content.get('stories', {}))} stories")

        # Step 2: Extract and clean text
        content = extract_text(content, corrections)
        logger.debug(f"  Category: {content.get('category')}, Model: {content.get('model')}")

        # Step 3: Extract specifications from tables
        specs = extract_tables(content.get('tables', []), field_mappings)
        logger.debug(f"  Extracted {len(specs)} SKU specifications")

        # Step 4: Write XLSX
        output_path = Path(output_dir) / f"{idml_path.stem}.xlsx"
        write_xlsx(content, specs, str(output_path))
        logger.info(f"  Output: {output_path}")

        return str(output_path)

    except Exception as e:
        logger.error(f"  Error processing {idml_path.name}: {e}")
        # Log to error file
        error_log = Path(output_dir).parent / 'errors' / f"{idml_path.stem}.log"
        error_log.parent.mkdir(parents=True, exist_ok=True)
        with open(error_log, 'w', encoding='utf-8') as f:
            f.write(f"Error: {e}\n")
            f.write(f"File: {idml_path}\n")
        return None


def process_directory(input_dir: str, output_dir: str, knowledge_dir: str = None) -> Dict:
    """Process all IDML files in a directory.

    Returns: Summary dict with counts
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load knowledge base
    field_mappings = {}
    corrections = {}
    if knowledge_dir:
        knowledge_path = Path(knowledge_dir)
        if knowledge_path.is_file():
            field_mappings = load_field_mappings(str(knowledge_path))
            corrections = load_corrections(str(knowledge_path.parent))
        else:
            field_mappings = load_field_mappings(str(knowledge_path / 'field_mappings.json'))
            corrections = load_corrections(str(knowledge_path))

    # Find IDML files
    idml_files = list(input_dir.glob('*.idml'))
    if not idml_files:
        logger.warning(f"No IDML files found in {input_dir}")
        return {'total': 0, 'success': 0, 'failed': 0}

    logger.info(f"Found {len(idml_files)} IDML files to process")

    # Process each file
    results = {
        'total': len(idml_files),
        'success': 0,
        'failed': 0,
        'files': []
    }

    for idml_file in idml_files:
        output_path = process_idml(
            str(idml_file),
            str(output_dir),
            field_mappings,
            corrections
        )

        if output_path:
            results['success'] += 1
            results['files'].append(output_path)
        else:
            results['failed'] += 1

    logger.info(f"Processing complete: {results['success']}/{results['total']} successful")
    return results


def main():
    parser = argparse.ArgumentParser(description='Extract data from IDML files to XLSX')

    parser.add_argument('--input', '-i', help='Input directory containing IDML files')
    parser.add_argument('--file', '-f', help='Single IDML file to process')
    parser.add_argument('--output', '-o', required=True, help='Output directory for XLSX files')
    parser.add_argument('--knowledge', '-k', help='Path to knowledge base (field_mappings.json or directory)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate arguments
    if not args.input and not args.file:
        parser.error("Either --input or --file is required")

    if args.file:
        # Process single file
        field_mappings = load_field_mappings(args.knowledge) if args.knowledge else {}
        knowledge_dir = str(Path(args.knowledge).parent) if args.knowledge else None
        corrections = load_corrections(knowledge_dir) if knowledge_dir else {}

        result = process_idml(args.file, args.output, field_mappings, corrections)
        sys.exit(0 if result else 1)
    else:
        # Process directory
        results = process_directory(args.input, args.output, args.knowledge)
        sys.exit(0 if results['failed'] == 0 else 1)


if __name__ == '__main__':
    main()
