"""
Log Loader

Loads authentication/security logs from CSV or JSON files.
Handles errors gracefully and raises custom exceptions for integration with validation pipeline.
"""

import json
import logging
from typing import Tuple, List, Dict, Any
from pathlib import Path
import pandas as pd

from validation import FileFormatError

# Optional: Set up logging (you can expand this later)
logger = logging.getLogger(__name__)


# ============================================================================
# MAIN LOADER FUNCTION
# ============================================================================

def load_logs(file_path: str) -> pd.DataFrame:
    """
    Load logs from a CSV or JSON file.

    Args:
        file_path: Path to the log file (.csv, .json, or .jsonl)

    Returns:
        pd.DataFrame with the loaded data

    Raises:
        FileFormatError: If the file cannot be read or parsed

    TODO: Step-by-step pseudocode below
    """

    # TODO Step 1: Validate file_path is a string and convert to Path object
    # Hint: use pathlib.Path(file_path)
    if file_path is None or not isinstance(file_path, str):
        raise FileFormatError(
            file_path=str(file_path),
            message="Invalid file path provided",
            error_code="invalid_path",
            original=None
        )
    else:
        file_path = Path(file_path)

    # TODO Step 2: Check file extension to determine how to parse
    # Hint: Use file_path.endswith('.csv') or str(file_path).endswith('.csv')
    try:
        if str(file_path).endswith('.csv'):
            df = pd.read_csv(file_path)
            return df
        elif str(file_path).endswith('.json'):
            df = pd.read_json(file_path)
            return df
        elif str(file_path).endswith('.jsonl'):
            df = pd.read_json(file_path, lines=True)
            return df
        else:
            raise FileFormatError(
                file_path=str(file_path),
                message='Unsupported_format. Expected .csv, json, or jsonl',
                error_code='unsupported_format',
                original=None
            )
    except (FileNotFoundError) as e:
        raise FileFormatError(
            file_path=str(file_path),
            message="File not found",
            error_code="file_not_found",
            original=e
        ) from e
    except (pd.errors.ParserError) as e:
        raise FileFormatError(
            file_path=str(file_path),
            message='Error parsing the contents of the file',
            error_code='parsing_error',
            original=e
        ) from e
    except (json.JSONDecodeError):
        raise FileFormatError(
            file_path=str(file_path),
            message=f'Detected an unexpected value: {e}',
            error_code='Unexpected Value',
            original=e
        ) from e
    except (UnicodeDecodeError):
        raise FileFormatError(
            file_path=str(file_path),
            message=f'Can not interpret using specified encoding scheme: {e}',
            error_code="Can't understand current encoding.",
            original=e
        ) from e
    except FileFormatError as e:
        logging.error('File format error')
        raise
    except Exception as e:
        raise FileFormatError(
            file_path=str(file_path),
            message="Unknown error occurred",
            error_code="unknown",
            original=e
        ) from e

    # TODO Step 3: Create a try/except block with multiple except clauses:
    #   - except FileNotFoundError -> raise FileFormatError with error_code='file_not_found'
    #   - except pd.errors.ParserError (for CSV) -> raise FileFormatError with error_code='csv_parse'
    #   - except json.JSONDecodeError (for JSON) -> raise FileFormatError with error_code='json_decode'
    #   - except UnicodeDecodeError -> raise FileFormatError with error_code='encoding'
    #   - except FileFormatError -> re-raise as-is
    #   - except Exception as e -> raise FileFormatError with error_code='unknown'

    # TODO Step 4: For CSV files, use pd.read_csv(file_path)
    # Hint: Catch pd.errors.ParserError, UnicodeDecodeError, FileNotFoundError

    # TODO Step 5: For JSON files, use json.load(open(file_path)) or similar
    # Hint: Catch json.JSONDecodeError, UnicodeDecodeError, FileNotFoundError
    # Hint: Can also support .jsonl (JSON Lines) - one JSON object per line

    # TODO Step 6: For unsupported file types, raise FileFormatError with error_code='unsupported_format'

    # TODO Step 7: For each raised FileFormatError, include:
    #   - file_path: str
    #   - message: str (human-readable, e.g., "CSV parsing failed")
    #   - error_code: str (machine-parseable, e.g., 'csv_parse')
    #   - original: the caught exception (use 'from e' to chain)

# ============================================================================
# HELPER: LOAD MULTIPLE FILES GRACEFULLY
# ============================================================================

def load_all_logs(file_paths: List[str]) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
    """
    Load multiple log files, skipping bad ones and accumulating errors.

    Args:
        file_paths: List of file paths to load

    Returns:
        Tuple of (combined_dataframe, list_of_error_dicts)
        - combined_dataframe: pd.DataFrame with all successfully loaded rows
        - list_of_error_dicts: List of error dicts (from FileFormatError.to_dict())

    TODO: Step-by-step pseudocode below
    """

    # TODO Step 1: Initialize two lists:
    #   - all_dataframes: to accumulate successful DataFrames
    #   - all_errors: to accumulate error dictionaries

    # TODO Step 2: Loop through each file_path in file_paths

    # TODO Step 3: Inside the loop, try to call load_logs(file_path)

    # TODO Step 4: If load_logs succeeds, append the returned DataFrame to all_dataframes

    # TODO Step 5: If FileFormatError is caught:
    #   - Append e.to_dict() to all_errors (this converts the exception to a dict for the report)
    #   - Log a warning: logger.warning(f"Skipping {file_path}: {e}")
    #   - Continue to the next file (don't crash)

    # TODO Step 6: After the loop, combine all DataFrames:
    #   - If all_dataframes is not empty, use pd.concat(all_dataframes, ignore_index=True)
    #   - If empty, return an empty DataFrame: pd.DataFrame()

    # TODO Step 7: Return a tuple: (combined_df, all_errors)

    all_dataframes = []
    all_errors = []

    for file_path in file_paths:
        if not file_path:
            continue # Continues so the remaining files load

        try:
            df = load_logs(str(file_path))
            all_dataframes.append(df)
        except FileFormatError as e:
            all_errors.append(e.to_dict())
            logger.warning("Skipping %s: %s", file_path, e)
            # logger.warning(f"Skipping {file_path}: {e}")
            continue
        except Exception as e:
            error_dict = {
                'file': str(file_path),
                'kind': 'unknown_error',
                'error_code': 'unknown',
                'message': str(e),
                'original_error': str(e)
            }
            all_errors.append(error_dict)

    if len(all_dataframes) != 0:
        combined_df = pd.concat(all_dataframes, ignore_index=True)
    else:
        return (pd.DataFrame(), all_errors) #returns tuple

    combined_tuple = (combined_df, all_errors)
    return combined_tuple
# ============================================================================
# HELPER: LOAD FROM DIRECTORY
# ============================================================================

def load_logs_from_directory(directory: str, pattern: str = "*.csv") -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
    """
    Load all log files from a directory matching a pattern.

    Args:
        directory: Path to directory
        pattern: Glob pattern (e.g., "*.csv", "*.json", "*")

    Returns:
        Tuple of (combined_dataframe, list_of_error_dicts)

    TODO: Hints
    - Use pathlib.Path(directory).glob(pattern) to find matching files
    - Convert Path objects to strings and call load_all_logs()
    """
    pass


# ============================================================================
# EXAMPLE USAGE (for your notebook)
# ============================================================================

"""
PSEUDOCODE: How to use the loader functions in your notebook:

# Single file
try:
    df = load_logs("sample_data/good.csv")
    print(f"Loaded {len(df)} rows")
except FileFormatError as e:
    print(f"Failed to load: {e}")

# Multiple files
files = ["sample_data/good.csv", "sample_data/messy.csv"]
df_combined, errors = load_all_logs(files)
print(f"Loaded {len(df_combined)} rows")
if errors:
    print(f"Encountered {len(errors)} file errors:")
    for error in errors:
        print(f"  - {error['file']}: {error['message']}")

# From directory
df, errors = load_logs_from_directory("sample_data", pattern="*.csv")
"""
