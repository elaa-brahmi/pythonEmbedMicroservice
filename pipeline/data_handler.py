import json
import os
from typing import Iterable, Generator

try:
    import ijson
except Exception:
    ijson = None


def stream_data(file_path: str) -> Iterable[dict]:
    """Yield records from a JSON file in a streaming fashion.

    Supports either a JSON array of objects ("[ {...}, {...} ]") or
    newline-delimited JSON (NDJSON). Uses `ijson` when available for
    low-memory parsing.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found")

    # Try streaming JSON array with ijson
    if ijson is not None:
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                for obj in ijson.items(f, "item"):
                    yield obj
                return
            except Exception:
                # Fall through to NDJSON fallback
                pass

    # NDJSON fallback
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                # Last resort: try to parse whole file as JSON array
                f.seek(0)
                data = json.load(f)
                if isinstance(data, list):
                    for obj in data:
                        yield obj
                    return
                raise


def load_data(file_path: str) -> list:
    """Convenience helper that loads the full file into memory (use with care).

    Prefer `stream_data()` for large files.
    """
    return list(stream_data(file_path))
