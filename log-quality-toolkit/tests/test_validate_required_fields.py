import sys
import os

src_path = os.path.join(os.path.dirname(__file__), "..", "src")
sys.path.insert(0, os.path.abspath(src_path))

from validation import validate_required_fields, SchemaError

test_records = [
    {"timestamp": "2025-01-01 12:00:00", "user": "alice"},        # GOOD
    {"user": "alice"},                                             # BAD - missing timestamp
    {"timestamp": "2025-01-01 12:00:00"},                         # BAD - missing user
    {"timestamp": None, "user": "alice"},                         # BAD - timestamp is None
    {"timestamp": "2025-01-01 12:00:00", "user": "alice", "event_id": "ev123"},  # GOOD - extra field ok
]

for record in test_records:
    try:
        result = validate_required_fields(record)
        print(f"{record}: OK")
    except SchemaError as e:
        print(f"{record}: SchemaError -> {e}")
    except Exception as e:
        print(f"{record}: Error -> {e}")