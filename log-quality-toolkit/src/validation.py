"""
Auth Log Schema & Validation

Defines the expected structure and validation rules for authentication/security logs.
"""

import json
import pandas as pd
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime


class TimestampParseError(Exception):
    """Custom exception for timestamp parsing errors."""
    pass


class SchemaError(Exception):
    """Custom exception for schema validation errors."""
    pass


class FileFormatError(Exception):
    """
    Custom exception for file format errors.

    Raised when a file cannot be read or parsed (e.g., malformed JSON, corrupt CSV, wrong encoding).

    Attributes:
        file_path: Path to the problematic file
        message: Human-readable error message
        error_code: Machine-parseable error type (e.g., 'json_decode', 'csv_parse', 'encoding')
        original: The original caught exception (for chaining)

    Example:
        try:
            data = json.load(file)
        except json.JSONDecodeError as e:
            raise FileFormatError(
                file_path="path/to/file.json",
                message="Invalid JSON syntax",
                error_code="json_decode",
                original=e
            ) from e
    """
    # TODO: Implement __init__ to accept and store file_path, message, error_code, original
    # TODO: Override __str__ to produce a readable message like:
    #       "FileFormatError [json_decode]: path/to/file.json - Invalid JSON syntax"
    # TODO: Consider adding a to_dict() method for serializing to the JSON quality report

    def __init__(self, file_path: str, message: str, error_code: str = None, original: Exception = None):
        self.file_path = file_path
        self.message = message
        self.error_code = error_code
        self.original = original
        super().__init__(
            f'FileFormatError [{error_code}]: {file_path} - {message}')

    def to_dict(self):
        """Convert to dictionary for JSON report serialization."""
        return {
            'file': self.file_path,
            'kind': 'file_format',
            'error_code': self.error_code,
            'message': self.message,
            'original_error': str(self.original) if self.original else None
        }

# Inherits from SchemaError
class user_error(SchemaError):
    """Custom exception that defines user generated errors."""
    pass


# class DataQualityError(Exception):
#     """Custom exception for data quality issues."""
#     pass


# ============================================================================
# AUTH LOG SCHEMA
# ============================================================================
AUTH_LOG_SCHEMA: Dict[str, Dict[str, Any]] = {
    # FULLY IMPLEMENTED FIELDS
    # -------------------------

    "timestamp": {
        "required": True,
        "type": "datetime",
        "description": "When the auth event occurred. Required for all records.",
        "formats": ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S.%f"],
    },

    "user": {
        "required": True,
        "type": "string",
        "description": "The user account that performed the action. Required for all records.",
        "constraints": {"min_length": 1, "max_length": 256},
    },

    "event_id": {
        "required": False,
        "type": "string",
        "description": "Unique identifier for the event. Optional; useful for tracking and deduplication.",
        # TODO: Define regex pattern if needed (e.g., alphanumeric + hyphens)
        "constraints": {"pattern": None},
    },


    # LEARNING NOTES FOR SELF-IMPLEMENTATION
    # ----------------------------------------

    # TODO: Define "src_ip" (source IP address) //import re for functionality
    "src_ip": {
        "required": False,
        "type": "string",
        "description": "The IP address from which the login/action originated.",
        "constraints": {"ipv4_pattern": r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"}
    },
    # Hints:
    # - required: False (it's optional)
    # - type: should be "string" or "ip_address"
    # - description: "The IP address from which the login/action originated."
    # - constraints: Consider adding a "pattern" for IPv4 validation (e.g., regex or ipaddress module check)

    # TODO: Define "dest_host" (destination host/server)
    "dest_host": {
        "required": False,
        "type": "string",
        "description": "The target host or service that was accessed.",
        "constraints": {"min_length": 1, "max_length": 255}
    },
    # Hints:
    # - required: False (it's optional)
    # - type: should be "string" (hostname or FQDN)
    # - description: "The target host or service that was accessed."
    # - constraints: Consider min/max length; consider hostname pattern validation
    # Example structure (see src_ip above as a template)

    # TODO: Define "action" (success/fail outcome)
    "action": {
        "required": False,
        "type": "enum",
        "description": "The outcome of the auth attempt (e.g., 'success', 'failure', 'blocked').",
        "allowed_values": ["success", "failure", "blocked"]
    },
    # Hints:
    # - required: False (it's optional)
    # - type: should be "string" or "enum"
    # - description: "The outcome of the auth attempt (e.g., 'success', 'failure', 'blocked')."
    # - constraints: Consider using an "allowed_values" or "enum" list to restrict to known outcomes

}


# ============================================================================
# VALIDATION HELPER FUNCTIONS (Placeholders)
# ============================================================================

def validate_timestamp(value: str) -> bool:
    """
    Validate that a timestamp string matches one of the acceptable formats.

    Args:
        value: Timestamp string to validate.

    Returns:
        True if valid, False otherwise.
    """
    # TODO: Implement using datetime.strptime() with formats from schema
    if not value or not isinstance(value, str):
        return TimestampParseError(f'Timestamp must not be a non-empty string. Got: {value}')

    formats = AUTH_LOG_SCHEMA['timestamp']['formats']

    for fmt in formats:
        try:
            datetime.strptime(value, fmt)
            return True
        except ValueError:
            continue

    raise TimestampParseError(
        f'Timestamp does not match any known formats: {formats}')


def validate_user(value: str) -> bool:
    """
    Validate that a user field is non-empty and within length constraints.

    Args:
        value: User string to validate.

    Returns:
        True if valid, False otherwise.
    """
    # TODO: Check min/max length from schema constraints

    #  Check if value is a string and meets length constraints
    if not isinstance(value, str):
        raise user_error(f'User must be a string, got {type(value)}')

    min_length = AUTH_LOG_SCHEMA['user']['constraints']['min_length']
    max_length = AUTH_LOG_SCHEMA['user']['constraints']['max_length']

    if not min_length <= len(value) <= max_length:
        raise user_error(
            f'User must be between {min_length} and {max_length} characters long.'
            f' Got length {len(value)}.'
        )
    return True


def validate_required_fields(record: Dict[str, Any]) -> bool:
    """
    Check that all required fields are present and non-null in a record.

    Args:
        record: A log record (dict) to validate.

    Returns:
        True if all required fields are present, False otherwise.
    """
    # TODO: Iterate over AUTH_LOG_SCHEMA, check record[field] is not None for required=True fields

    for field, props in AUTH_LOG_SCHEMA.items():
        if props['required'] is True:
            if field not in record or record[field] is None:
                raise SchemaError(f'Missing required field: {field}')
    return True

# ============================================================================
# VALIDATE AND CLEAN DATAFRAME
# ============================================================================

def validate_and_clean(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Validate and clean a DataFrame of auth logs using the schema.
    
    Loops through each row and applies validation functions. Quarantines bad rows
    and collects quality metrics.
    
    Args:
        df: DataFrame with auth log data
    
    Returns:
        Tuple of (clean_df, issues_dict)
        - clean_df: DataFrame with only valid rows
        - issues_dict: Dict with counts/summaries:
            - total_rows: int
            - bad_rows: int
            - bad_rows_list: list of (index, reason) tuples
            - timestamp_errors: int
            - missing_required_fields: int
            - null_rates: dict with null % per column
    
    TODO: Step-by-step implementation below
    """
    
    # TODO Step 1: Initialize tracking structures
    #   - clean_rows: list to accumulate valid rows
    #   - bad_rows_list: list of (row_index, error_message) tuples for quarantined rows
    #   - error_counts: dict to count error types (e.g., 'timestamp_errors': 0, 'schema_errors': 0)
    
    # TODO Step 2: Loop through DataFrame rows using df.iterrows() or df.itertuples()
    #   - For each row, extract fields: timestamp, user, src_ip, dest_host, action, event_id
    #   - Build a record dict: {'timestamp': ..., 'user': ..., ...}
    
    # TODO Step 3: Inside the loop, validate each row using your helper functions
    #   Try in this order:
    #   a) validate_required_fields(record) — catches missing/None required fields
    #      If exception: increment error_counts['missing_required_fields'], append to bad_rows_list, continue
    #   b) validate_timestamp(record['timestamp']) — catches invalid timestamp formats
    #      If exception: increment error_counts['timestamp_errors'], append to bad_rows_list, continue
    #   c) validate_user(record['user']) — catches invalid user strings
    #      If exception: increment error_counts['schema_errors'], append to bad_rows_list, continue
    
    # TODO Step 4: If all validations pass, append the row (as dict or Series) to clean_rows
    
    # TODO Step 5: After the loop, reconstruct clean DataFrame from clean_rows
    #   - Use pd.DataFrame(clean_rows) to rebuild, or concat
    #   - Reset index if needed
    
    # TODO Step 6: Calculate quality metrics for issues_dict
    #   - total_rows: len(df)
    #   - clean_rows_count: len(clean_df)
    #   - bad_rows: total_rows - clean_rows_count
    #   - null_rates: for each column, calculate % of nulls
    #       Hint: df.isnull().sum() / len(df) * 100
    
    # TODO Step 7: Build and return issues_dict
    #   issues_dict = {
    #       'total_rows': ...,
    #       'clean_rows': ...,
    #       'bad_rows': ...,
    #       'bad_rows_list': [...],
    #       'error_counts': {...},
    #       'null_rates': {...}
    #   }
    #   return (clean_df, issues_dict)

    clean_rows = []
    bad_rows_list: List[Dict[str, any]] = [] #Create list with type annotation
    error_counts = {
        'missing_required_fields': 0,
        'timestamp_errors': 0,
        'user_errors': 0,
        'src_ip_errors': 0,
        'action_errors': 0,
        'other_schema_errors': 0
    }

    for row in df.itertuples():
        record = {
            # key: value
            'timestamp': row.timestamp,
            'user': row.user,
            'src_ip': row.src_ip,
            'dest_host': row.dest_host,
            'id': row.action_id,
            'action': row.action
        }

        try:
            validate_required_fields(record)
            validate_timestamp(record['timestamp'])
            validate_user(record['user'])

            clean_rows.append(record)

        except SchemaError as e:
            error_counts['missing_required_fields'] += 1
            message = str(e)
            field = None

            if message.startswith("Missing required field:"):
                candidate = message.split(":", 1)[1].strip()
                if candidate in AUTH_LOG_SCHEMA:
                    field = candidate

            bad_rows_list.append({
                'row_index': row.Index,
                'field': field,
                'error_type': 'missing_required_fields',
                'message': message,
                'record_preview': {
                    'timestamp': record.get('timestamp'),
                    'user': record.get('user'),
                    'src_ip': record.get('src_ip')
                }
            })

            continue

        # except 

# ============================================================================
# FileFormatError USAGE PSEUDOCODE (for src/loader.py)
# ============================================================================

"""
PSEUDOCODE: Where FileFormatError gets raised in loader.py

In src/loader.py, you'll have a load_logs(file_path) function that looks roughly like:

    def load_logs(file_path: str) -> pd.DataFrame:
        '''Load logs from CSV or JSON file.'''
        try:
            if file_path.endswith('.csv'):
                # TODO: Try to read CSV
                # Catch pd.errors.ParserError -> raise FileFormatError(..., 'csv_parse')
                # Catch UnicodeDecodeError -> raise FileFormatError(..., 'encoding')
                # Catch FileNotFoundError -> raise FileFormatError(..., 'file_not_found')
                df = pd.read_csv(file_path)
                return df
            
            elif file_path.endswith('.json') or file_path.endswith('.jsonl'):
                # TODO: Try to read JSON/JSONL
                # Catch json.JSONDecodeError -> raise FileFormatError(..., 'json_decode')
                # Catch FileNotFoundError -> raise FileFormatError(..., 'file_not_found')
                with open(file_path) as f:
                    data = json.load(f)
                df = pd.DataFrame(data)
                return df
            
            else:
                # TODO: Unsupported file type
                raise FileFormatError(
                    file_path=file_path,
                    message=f"Unsupported file type: {file_path}",
                    error_code="unsupported_format"
                )
        
        except FileFormatError:
            # Re-raise our custom exceptions as-is
            raise
        
        except FileNotFoundError as e:
            # TODO: Wrap file-not-found errors
            raise FileFormatError(
                file_path=file_path,
                message=f"File not found",
                error_code="file_not_found",
                original=e
            ) from e
        
        except Exception as e:
            # TODO: Catch any other unexpected error and wrap
            raise FileFormatError(
                file_path=file_path,
                message=f"Unexpected error reading file",
                error_code="unknown",
                original=e
            ) from e


AT A HIGHER LEVEL (in your pipeline or notebook), catching FileFormatError:

    def load_all_logs_gracefully(file_list):
        '''Load multiple files, skip bad ones.'''
        all_data = []
        errors = []
        
        for file_path in file_list:
            try:
                df = load_logs(file_path)  # Raises FileFormatError on failure
                all_data.append(df)
            
            except FileFormatError as e:
                # TODO: Record the error for the quality report
                errors.append(e.to_dict())  # Requires to_dict() method
                logging.warning(f"Skipping {file_path}: {e}")
                # Continue with next file instead of crashing
                continue
        
        # Combine all successful dataframes
        final_df = pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
        
        return final_df, errors
"""
