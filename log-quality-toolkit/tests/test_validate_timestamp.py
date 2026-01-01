import sys
import os

# Navigate to src folder relative to this test file's location
src_path = os.path.join(os.path.dirname(__file__), "..", "src")
sys.path.insert(0, os.path.abspath(src_path))

from validation import validate_timestamp, TimestampParseError

tests = [
    "2025-01-02 15:04:05",
    "2025-01-02T15:04:05Z",
    "2025-01-02 15:04:05.123456",
    "not-a-timestamp",
]

for t in tests:
    try:
        result = validate_timestamp(t)
        print(f"{t!r}: OK -> {result}")
    except TimestampParseError as e:
        print(f"{t!r}: TimestampParseError -> {e}")
    except Exception as e:
        print(f"{t!r}: Error -> {e}")