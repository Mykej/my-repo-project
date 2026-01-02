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
    12345,      # Not a string
]

for u in tests:
    try:
        result = validate_user(u)
        print(f"{u!r}: OK -> {result}")
    except SchemaError:
        print(f"{u!r}: SchemaError -> {u} is either not a string or does not meet length constraints.")

