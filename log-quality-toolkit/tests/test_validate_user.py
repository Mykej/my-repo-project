import sys
import os

# Navigate to src folder relative to this test file's location
src_path = os.path.join(os.path.dirname(__file__), "..", "src")
sys.path.insert(0, os.path.abspath(src_path))

from validation import validate_user, SchemaError

tests = [
    "alice",
    "bob",
    "charlie",
    "",
    "a" * 257,  # Too long
]

for u in tests:
    try:
        result = validate_user(u)
        print(f"{u!r}: OK -> {result}")
    except SchemaError as e:
        print(f"{u!r}: SchemaError -> {e}")
    except Exception as e:
        print(f"{u!r}: Error -> {e}")
