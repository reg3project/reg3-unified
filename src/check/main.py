#!/usr/bin/env python3
"""
REG3 Check - Compare extracted XLSX against reference files

Usage:
    python main.py --extracted output/xlsx/learning --reference input/xlsx/learning --reports reports/per-file
    python main.py --extracted output/xlsx/learning/B614.xlsx --reference input/xlsx/learning/B614.xlsx
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional

from xlsx_loader import load_xlsx, load_xlsx_pair
from comparator import Comparator, compare_files
from reporter import Reporter, generate_reports

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def compare_single_file(
    extracted_path: str,
    reference_path: str,
    report_dir: Optional[str] = None
) -> Dict:
    """Compare a single extracted file against reference.

    Returns: Comparison result dict
    """
    extracted_path = Path(extracted_path)
    reference_path = Path(reference_path)

    logger.info(f"Comparing: {extracted_path.name}")

    try:
        # Load both files
        extracted, reference = load_xlsx_pair(str(extracted_path), str(reference_path))

        # Compare
        comparison = compare_files(extracted, reference, extracted_path.stem)
        result = comparison.to_dict()

        logger.info(f"  Accuracy: {result['accuracy']}%")
        logger.info(f"  Matches: {result['matches']}, Mismatches: {result['mismatches']}")

        # Generate report if output dir specified
        if report_dir:
            reporter = Reporter(report_dir)
            report_path = reporter.generate_file_report(result)
            logger.info(f"  Report: {report_path}")

        return result

    except FileNotFoundError as e:
        logger.error(f"  File not found: {e}")
        return {
            'file': extracted_path.stem,
            'error': str(e),
            'accuracy': 0,
            'matches': 0,
            'mismatches': 0,
        }
    except Exception as e:
        logger.error(f"  Error comparing: {e}")
        return {
            'file': extracted_path.stem,
            'error': str(e),
            'accuracy': 0,
            'matches': 0,
            'mismatches': 0,
        }


def compare_directories(
    extracted_dir: str,
    reference_dir: str,
    report_dir: str
) -> Dict:
    """Compare all files in extracted directory against reference.

    Returns: Summary dict
    """
    extracted_dir = Path(extracted_dir)
    reference_dir = Path(reference_dir)
    report_dir = Path(report_dir)

    # Find extracted files
    extracted_files = list(extracted_dir.glob('*.xlsx'))
    if not extracted_files:
        logger.warning(f"No XLSX files found in {extracted_dir}")
        return {'total': 0, 'comparisons': []}

    logger.info(f"Found {len(extracted_files)} extracted files to compare")

    # Compare each file
    comparisons = []
    total_matches = 0
    total_mismatches = 0

    for ext_file in extracted_files:
        # Find matching reference file
        ref_file = reference_dir / ext_file.name

        if not ref_file.exists():
            logger.warning(f"  No reference file for {ext_file.name}")
            continue

        result = compare_single_file(
            str(ext_file),
            str(ref_file),
            str(report_dir)
        )

        comparisons.append(result)
        total_matches += result.get('matches', 0)
        total_mismatches += result.get('mismatches', 0)

    # Calculate overall accuracy
    total = total_matches + total_mismatches
    overall_accuracy = 0
    if total > 0:
        overall_accuracy = round((total_matches / total) * 100, 2)

    # Generate summary report
    if comparisons:
        summary_path = report_dir.parent / 'summary.html'
        reporter = Reporter(str(report_dir.parent))
        reporter.generate_summary(comparisons, str(summary_path))
        logger.info(f"Summary report: {summary_path}")

    logger.info(f"\nOverall accuracy: {overall_accuracy}%")
    logger.info(f"Total matches: {total_matches}, Total mismatches: {total_mismatches}")

    return {
        'total': len(comparisons),
        'overall_accuracy': overall_accuracy,
        'total_matches': total_matches,
        'total_mismatches': total_mismatches,
        'comparisons': comparisons,
    }


def main():
    parser = argparse.ArgumentParser(description='Compare extracted XLSX against reference')

    parser.add_argument('--extracted', '-e', required=True,
                        help='Extracted XLSX file or directory')
    parser.add_argument('--reference', '-r', required=True,
                        help='Reference XLSX file or directory')
    parser.add_argument('--reports', '-o',
                        help='Output directory for reports')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    extracted_path = Path(args.extracted)
    reference_path = Path(args.reference)

    # Determine if comparing single file or directory
    if extracted_path.is_file():
        # Single file comparison
        result = compare_single_file(
            str(extracted_path),
            str(reference_path),
            args.reports
        )
        print(json.dumps(result, indent=2))
        sys.exit(0 if result.get('accuracy', 0) >= 95 else 1)
    else:
        # Directory comparison
        if not args.reports:
            parser.error("--reports is required for directory comparison")

        results = compare_directories(
            str(extracted_path),
            str(reference_path),
            args.reports
        )

        # Write comparison log
        log_path = Path(args.reports).parent / 'comparison.log'
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"\nOverall accuracy: {results['overall_accuracy']}%\n")

        sys.exit(0 if results['overall_accuracy'] >= 95 else 1)


if __name__ == '__main__':
    main()
