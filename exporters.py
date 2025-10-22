"""
Data export utilities for permit data.
"""
import json
import csv
import logging
from typing import List, Dict, Any
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)


class PermitExporter:
    """Export permit data to various formats."""

    @staticmethod
    def to_json(permits: List[Dict[str, Any]], output_path: str, pretty: bool = True) -> bool:
        """
        Export permits to JSON file.

        Args:
            permits: List of permit dictionaries
            output_path: Path to output JSON file
            pretty: Pretty-print JSON (default: True)

        Returns:
            True if successful, False otherwise
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                if pretty:
                    json.dump(permits, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(permits, f, ensure_ascii=False)

            logger.info(f"Exported {len(permits)} permits to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export to JSON: {e}")
            return False

    @staticmethod
    def to_csv(permits: List[Dict[str, Any]], output_path: str) -> bool:
        """
        Export permits to CSV file.

        Args:
            permits: List of permit dictionaries
            output_path: Path to output CSV file

        Returns:
            True if successful, False otherwise
        """
        try:
            if not permits:
                logger.warning("No permits to export")
                return False

            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Get all unique field names
            fieldnames = set()
            for permit in permits:
                fieldnames.update(permit.keys())
            fieldnames = sorted(fieldnames)

            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(permits)

            logger.info(f"Exported {len(permits)} permits to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export to CSV: {e}")
            return False

    @staticmethod
    def to_excel(permits: List[Dict[str, Any]], output_path: str, sheet_name: str = 'Permits') -> bool:
        """
        Export permits to Excel file.

        Args:
            permits: List of permit dictionaries
            output_path: Path to output Excel file
            sheet_name: Name of the Excel sheet (default: 'Permits')

        Returns:
            True if successful, False otherwise
        """
        try:
            if not permits:
                logger.warning("No permits to export")
                return False

            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            df = pd.DataFrame(permits)
            df.to_excel(output_path, sheet_name=sheet_name, index=False)

            logger.info(f"Exported {len(permits)} permits to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export to Excel: {e}")
            return False

    @staticmethod
    def to_dataframe(permits: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Convert permits to pandas DataFrame.

        Args:
            permits: List of permit dictionaries

        Returns:
            pandas DataFrame
        """
        return pd.DataFrame(permits)

    @staticmethod
    def generate_summary(permits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary of the scraped permits.

        Args:
            permits: List of permit dictionaries

        Returns:
            Summary dictionary with statistics
        """
        if not permits:
            return {
                'total_permits': 0,
                'error': 'No permits to summarize'
            }

        df = pd.DataFrame(permits)

        summary = {
            'total_permits': len(permits),
            'fields': list(df.columns),
            'missing_data': {}
        }

        # Calculate missing data percentage for each field
        for column in df.columns:
            missing_count = df[column].isna().sum()
            if missing_count > 0:
                summary['missing_data'][column] = {
                    'count': int(missing_count),
                    'percentage': round((missing_count / len(permits)) * 100, 2)
                }

        # Add permit type breakdown if available
        if 'permit_type' in df.columns:
            summary['permit_types'] = df['permit_type'].value_counts().to_dict()

        # Add status breakdown if available
        if 'status' in df.columns:
            summary['status_counts'] = df['status'].value_counts().to_dict()

        # Add date range if issue_date is available
        if 'issue_date' in df.columns:
            try:
                dates = pd.to_datetime(df['issue_date'], errors='coerce')
                valid_dates = dates.dropna()
                if not valid_dates.empty:
                    summary['date_range'] = {
                        'earliest': str(valid_dates.min()),
                        'latest': str(valid_dates.max())
                    }
            except Exception as e:
                logger.debug(f"Failed to parse dates: {e}")

        return summary

    @staticmethod
    def save_summary(summary: Dict[str, Any], output_path: str) -> bool:
        """
        Save summary to JSON file.

        Args:
            summary: Summary dictionary
            output_path: Path to output JSON file

        Returns:
            True if successful, False otherwise
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)

            logger.info(f"Summary saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save summary: {e}")
            return False
